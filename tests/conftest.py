import os
import subprocess

from bs4 import BeautifulSoup
from flask import current_app

import pytest
from alembic.command import upgrade
from alembic.config import Config
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import sqlalchemy

from app import create_app, db as _db, get_env
from tests.db import create_event, create_event_type, create_fee

TEST_DATABASE_URI = os.environ['DATABASE_URL_{}'.format(get_env())] + '_test'


@pytest.yield_fixture(scope='session')
def app():
    _app = create_app(**{
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'PREFERRED_URL_SCHEME': 'http',
    })

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    assert _db.engine.url.database.endswith('_test'), 'dont run tests against main db'

    create_test_db_if_does_not_exist(_db)

    Migrate(app, _db)
    Manager(_db, MigrateCommand)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    ALEMBIC_CONFIG = os.path.join(BASE_DIR, 'migrations')
    config = Config(ALEMBIC_CONFIG + '/alembic.ini')
    config.set_main_option("script_location", ALEMBIC_CONFIG)

    with app.app_context():
        upgrade(config, 'head')

    yield _db

    _db.session.remove()
    _db.get_engine(app).dispose()


@pytest.fixture(scope='function')
def db_session(db):
    yield db

    db.session.remove()
    for tbl in reversed(db.metadata.sorted_tables):
        # if tbl.name not in ["fees"]:
        db.engine.execute(tbl.delete())
    db.session.commit()


@pytest.fixture(scope='function')
def sample_event(db):
    return create_event(title='test_title', description='test description')


@pytest.fixture(scope='function')
def sample_event_type(db, sample_fee):
    return create_event_type(event_type='short course', fee_id=sample_fee.id)


@pytest.fixture(scope='function')
def sample_fee(db):
    return create_fee(fee=5, conc_fee=3)


def create_test_db_if_does_not_exist(db):
    try:
        conn = db.engine.connect()
        conn.close()

    except sqlalchemy.exc.OperationalError as e:
        if 'database "{}" does not exist'.format(TEST_DATABASE_URI.split('/')[-1:][0]) in e.message:
            db_url = sqlalchemy.engine.url.make_url(TEST_DATABASE_URI)
            dbname = db_url.database

            if db_url.drivername == 'postgresql':
                subprocess.call(['/usr/bin/env', 'createdb', dbname])
        else:
            raise


def request(url, method, data=None):
    r = method(url, data=data)
    r.soup = BeautifulSoup(r.get_data(as_text=True), 'html.parser')
    return r
