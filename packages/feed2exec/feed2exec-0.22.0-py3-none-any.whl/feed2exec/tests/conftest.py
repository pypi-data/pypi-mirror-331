import logging
import logging.handlers

import betamax
import pytest

import feed2exec.plugins.maildir
from feed2exec.controller import FeedManager

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'feed2exec/tests/cassettes/'
    # config.default_cassette_options['record_mode'] = 'new_episodes'


@pytest.fixture()
@pytest.mark.usefixtures('betamax_parametrized_recorder')
def feed_manager_recorder(tmpdir_factory, betamax_parametrized_recorder):
    conf_path = tmpdir_factory.mktemp('config').join('feed2exex.ini')
    db_path = tmpdir_factory.mktemp('db').join('feed2exec.db')
    return (
            betamax_parametrized_recorder,
            FeedManager(
                        str(conf_path),
                        str(db_path),
                        session=betamax_parametrized_recorder.session
            )
    )


@pytest.fixture()
@pytest.mark.usefixtures('betamax_parametrized_session')
def feed_manager(tmpdir_factory, betamax_parametrized_session):
    conf_path = tmpdir_factory.mktemp('config').join('feed2exex.ini')
    db_path = tmpdir_factory.mktemp('db').join('feed2exec.db')
    return FeedManager(str(conf_path), str(db_path), session=betamax_parametrized_session)


@pytest.fixture()
def feed_manager_networked(tmpdir_factory):
    """like feed_manager, but doing actual network requests"""
    conf_path = tmpdir_factory.mktemp('config').join('feed2exex.ini')
    db_path = tmpdir_factory.mktemp('db').join('feed2exec.db')
    return FeedManager(str(conf_path), str(db_path))


@pytest.fixture(autouse=True)
def static_boundary(monkeypatch):
    monkeypatch.setattr(feed2exec.email, 'boundary',
                        '===============testboundary==')


@pytest.fixture()
def logging_handler():
    handler = logging.handlers.MemoryHandler(0)
    handler.setLevel('INFO')
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel('DEBUG')
    return handler
