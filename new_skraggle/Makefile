# RUN FLASK DEVELOPMENT SERVER
start:
	flask run

# RUN TESTS
unit-tests:
	python3 -m pytest ./src/tests/unit/ --disable-warnings

integration-tests:
	python3 -m pytest ./src/tests/integration/ --disable-warnings

all-tests:
	python3 -m pytest ./src/tests/ --disable-warnings

# INITIALIZE MODEL-DB SYNC
db-init:
	flask db init

# RUN MIGRATIONS
migrate:
	flask db migrate

# RUN DB UPGRADE
db-upgrade:
	flask db upgrade

db-relink:
	bash scripts/relink_migrations.sh

test-auth:
	python3 -m pytest ./skraggle/tests/integration/ --disable-warnings -k 'test_admin_auth'