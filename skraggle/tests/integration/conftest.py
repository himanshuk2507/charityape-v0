from subprocess import run as run_script
from subprocess import PIPE

import pytest
from skraggle.main import app
from skraggle.config import db
from skraggle.config import engine
from sqlalchemy import MetaData


def pytest_configure(config):
    print("\n\n ******** RUNNING MIGRATIONS IN TEST ENV ********* \n\n")
    app.config['TESTING'] = True

    run_script(["flask", "db", "upgrade", "-d", "./skraggle/migrations"], stdout=PIPE, text=True)


@pytest.fixture(scope='session')
def test_client():
    # first, create a test-app client
    with app.test_client() as test_client:
        # move the current scope in the app context
        with app.app_context():
            yield test_client

    drop_tables()


def drop_tables():
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine, checkfirst=True)
    engine.dispose()