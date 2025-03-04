#!/usr/bin/python3

import argparse
import logging
import os.path
import re
import subprocess
import sys
from datetime import datetime
from socket import gethostname
from urllib.parse import urlparse
from typing import Union


def _find_source(source_directory, link):
    """with the given URL for a Ikiwiki post, find the source file

    This also returns the "basename" as seen from the source
    directory, to make it easier to commit the file into git later.
    """
    try:
        item_url = urlparse(link)
    except ValueError as e:
        logging.error("cannot parse item link %s: %s", link, e)
        return False
    source_path = os.path.join(source_directory, item_url.path.strip("/"))
    for ext in (".md", ".mdwn"):
        if os.path.exists(source_path + ext):
            source_path = source_path + ext
            source_basename = item_url.path.strip("/")
            return source_path, source_basename
    else:
        logging.warning(
            "could not find source for %s, tried %s with .md and .mdwn extensions",
            link,
            source_path,
        )
        return None, None


def _add_directive(
    source_directory, source_path, source_basename, post_url, simulate=False
):
    """add the mastodon directive to a ikiwiki post, commit and push"""
    logging.info("adding mastodon directive to post")
    now = datetime.now().isoformat()
    with open(source_path, "a", encoding="utf-8") as fp:
        fp.write("\n\n")
        fp.write(f"<!-- posted to the federation on {now} -->\n")
        fp.write(f'[[!mastodon "{post_url}"]]')
    if not fp.closed:
        logging.warning("could not write to file %s", source_path)

    logging.info("adding toot URL %s and committing to git", post_url)
    commit_message = f"automatic federated post of {source_basename}\n\n"
    commit_message += f"Command: {sys.argv}\n"
    commit_message += f"Plugin file: {__file__}\n"
    commit_message += f"Source directory: {source_directory}\n"
    commit_message += "Running on: " + gethostname() + "\n"

    try:
        # TODO: make quiet when this works (unless verbose)
        subprocess.check_call(
            (
                "git",
                "-C",
                source_directory,
                "commit",
                "-m",
                commit_message,
                source_path,
            )
        )
        if simulate:
            logging.warning("committed, but not pushed because simulate")
        else:
            logging.info("pushing commit")
            subprocess.check_call(("git", "-C", source_directory, "push"))
    except subprocess.CalledProcessError as e:
        logging.warning("failed to commit and push to git: %s", e)


def toot(post_body: str, simulate: bool):
    # construct the final post text body
    logging.info("posting toot: %s", post_body)
    command = ("toot", "post", "--visibility", "public", post_body)
    logging.debug(
        "calling command: %s%s",
        command,
        " (simulated)" if simulate else "",
    )
    if simulate:
        return "http://example.com/simulated"
    try:
        ret = subprocess.run(command, stdout=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        logging.error("failed to post toot: %s", e)
        return False
    if ret.returncode != 0:
        logging.error(
            "failed to post toot, command failed with status %d", ret.returncode
        )
        return False
    # normal output:
    # Toot posted: https://kolektiva.social/@Anarcat/109722626808467826
    _, _, post_url = ret.stdout.decode("utf-8").strip().split(maxsplit=2)

    return post_url


def make_post_body(item) -> str:
    # extract actual strings from the feedparser tags data structure
    tags = [t.get("label") or t.get("term") for t in item.tags]
    # prepend a hash sign if there is an actual tag
    tags_str = " ".join(["#" + str(t) for t in tags if t])
    # construct the final post text body
    return f"{item.title} {item.link} {tags_str}"


# cargo-culted from Ikiwiki.pm, preprocess sub
DIRECTIVE_REGEX = re.compile(
    r'''
            (\\?)        # 1: escape?
            \[\[(!)        # directive open; 2: prefix
            ([-\w]+)    # 3: command
            (        # 4: the parameters..
                \s+    # Must have space if parameters present
                (?:
                    (?:[-.\w]+=)?        # named parameter key?
                    (?:
                        """.*?"""    # triple-quoted value
                        |
                        "[^"]*?"    # single-quoted value
                        |
                        \'\'\'.*?\'\'\'    # triple-single-quote
                        |
                        <<([a-zA-Z]+)\n # 5: heredoc start
                        (?:.*?)\n\5    # heredoc value
                        |
                        [^"\s\]]+    # unquoted value
                    )
                    \s*            # whitespace or end
                                # of directive
                )
            *)?        # 0 or more parameters
            \]\]        # directive closed
''',
    re.VERBOSE | re.DOTALL | re.MULTILINE,
)

PARAM_REGEX = re.compile(
    r'''
(?:([-.\w]+)=)?    # 1: named parameter key?
(?:
    """(.*?)"""    # 2: triple-quoted value
|
    "([^"]*?)"      # 3: single-quoted value
|
    \'\'\'(.*?)\'\'\'     # 4: triple-single-quote
|
    <<([a-zA-Z]+)\n # 5: heredoc start
    (.*?)\n\5       # 6: heredoc value
|
    (\S+)           # 7: unquoted value
)
    (?:\s+|$)               # delimiter to next param
''',
    re.VERBOSE | re.DOTALL | re.MULTILINE,
)


def parse_ikiwiki_directives(path: str) -> dict[str, dict[Union[str, int], str]]:
    with open(path) as fp:
        content = fp.read()

    meta = {}
    for m in DIRECTIVE_REGEX.finditer(content):
        # escape = m.group(1)
        # prefix = m.group(2)
        command = m.group(3)
        params_blob = m.group(4)
        params = {}
        count: int = 0
        for pm in PARAM_REGEX.finditer(params_blob):
            if pm.group(1):
                i = pm.group(1)
            else:
                i = count
            params[i] = (
                pm.group(2) or pm.group(3) or pm.group(4) or pm.group(6) or pm.group(7)
            )
            if not pm.group(1):
                count += 1

        logging.debug("found directive %s with params %s", command, params)
        meta[command] = params
    return meta


def find_git_repo(path: str):
    assert path.startswith("/")
    while path:
        path = os.path.dirname(path)
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path.rstrip("/")


def post_and_write(
    post_path: str,
    base_url: str,
    simulate: bool,
    required_tags: list[str],
    required_prefix: list[str],
):
    logging.info("inspecting post path %s...", post_path)
    git_repo_path = find_git_repo(os.path.abspath(post_path))
    # remove .md(wn)? suffix
    source_basename, _ = post_path.removeprefix(git_repo_path).rsplit(".", maxsplit=1)
    post_url = base_url.rstrip("/") + "/" + source_basename.strip("/")

    logging.debug(
        "git_repo: %s, source_base: %s, post_url: %s",
        git_repo_path,
        source_basename,
        post_url,
    )
    meta = parse_ikiwiki_directives(post_path)
    if meta.get("mastodon"):
        logging.warning("already posted to %s", list(meta["mastodon"].values()).pop())
        return False

    title = meta.get("meta", {}).get("title", source_basename)
    tags = list(meta.get("tag", {}).values()) + list(meta.get("taglink", {}).values())
    common_tags = list(set(tags) & set(required_tags))
    logging.debug("common tags: %s, tags: %s", common_tags, tags)
    matching_prefixes = []
    for prefix in required_prefix:
        if source_basename.lstrip("/").startswith(prefix.strip("/")):
            matching_prefixes.append(prefix)
    if not common_tags and not matching_prefixes:
        errors = []
        if not matching_prefixes:
            errors.append("prefix (%s)" % " ".join(required_prefix))
        if not common_tags:
            errors.append("tags (%s)" % " ".join(required_tags))
        logging.warning(
            "ignoring article %s with tags %s, missing %s",
            source_basename,
            tags,
            ", ".join(errors),
        )
        return False
    if common_tags:
        logging.info("posting because of matching tags %s", ",".join(common_tags))
    if matching_prefixes:
        logging.info(
            "posting because of matching prefixes %s", ",".join(matching_prefixes)
        )

    tags_str = " ".join(["#" + t for t in tags if t])
    post_body = f"{title} {post_url} {tags_str}"
    toot_url = toot(post_body, simulate)
    if not toot_url:
        return False
    _add_directive(git_repo_path, post_path, source_basename, toot_url, simulate)


def output(*args, feed=None, item=None, **kwargs):
    """The toot plugin will take the given feed and pass it to the toot command

    This will generally post the update on a Mastodon server already preconfigured.

    This is *not* a standalone implementation of the Mastodon
    protocol, and is specifically tailored for integrating Mastodon
    comments inside a statically generated blog.

    In particular, it expects a "args" to point to the Ikiwiki source
    directory (not the bare repository!) where it can find the source
    file of the blog post and add the [[!mastodon]] directive so that
    comments are properly displayed.

    If no args is provided, the post is pushed without touching
    ikiwiki, but will give a warning. Use args=/dev/null to eliminate
    the warning.
    """
    try:
        source_directory = args[0]
    except IndexError:
        logging.warning(
            "no source directory provided in args, add args=/path/to/source/ to your config"
        )
        return False
    if source_directory == "/dev/null":
        source_directory = None
    if not os.path.isdir(source_directory):
        logging.warning("source directory %s not found, skipping ikiwiki editing")
        source_directory = None

    # find source file associated with the given link
    if source_directory:
        source_path, source_basename = _find_source(source_directory, item.link)

    post_body = make_post_body(item)
    post_url = toot(post_body)
    if not source_directory:
        print(f"posted '{post_body}' as {post_url}")
        return True

    _add_directive(source_directory, source_path, source_basename, post_url)
    # TODO: make quiet when this works reliably (unless verbose)
    print(f"posted '{post_body}' as {post_url}, metadata added to {source_path}")
    return True


def find_working_tree(bare_repo: str):
    bare_repo = bare_repo.rstrip("/")
    assert bare_repo.endswith(".git")
    parent = os.path.dirname(bare_repo)
    working_tree = os.path.join(parent, bare_repo.removesuffix(".git"))
    assert parent != working_tree
    return working_tree


def main():
    logging.basicConfig(level="DEBUG", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--post-path")
    group.add_argument("--post-receive", action="store_true")
    parser.add_argument("--tag", nargs="+", default=["blog"])
    parser.add_argument("--path-prefix", nargs="+", default=["blog/"])
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()
    if args.post_path:
        post_and_write(args.post_path, args.base_url, args.simulate, args.tag, args.path_prefix)
    else:
        logging.info("reading refs from stdin...")
        git_repo = os.path.abspath(os.environ.get("GIT_DIR", ".")).rstrip("/")
        logging.debug("GIT_DIR: %s", git_repo)
        if git_repo.endswith(".git"):
            working_tree = os.path.abspath(find_working_tree(git_repo))
            logging.debug("working tree: %s", working_tree)
        else:
            working_tree = None
        for line in sys.stdin.readlines():
            old, new, refname = line.split(maxsplit=2)
            cmd = ["git", "diff", "--name-only", old, new]
            logging.info("checking for changed files with: %s", cmd)
            ret = subprocess.run(cmd, encoding="utf-8", stdout=subprocess.PIPE)
            for path in ret.stdout.split("\n"):
                if not path:
                    continue
                logging.debug("changed file: %s", path)
                post_path = os.path.abspath(os.path.join(git_repo, path))
                if working_tree and not os.path.exists(post_path):
                    logging.info("not found in GIT_DIR, looking in working tree")
                    post_path = os.path.abspath(os.path.join(working_tree, path))
                post_and_write(post_path, args.base_url, args.simulate, args.tag, args.path_prefix)


if __name__ == "__main__":
    main()
