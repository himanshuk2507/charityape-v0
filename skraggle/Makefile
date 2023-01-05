# RUN FLASK DEVELOPMENT SERVER
start:
	cd .. && flask run

# RUN TESTS
unit-tests:
	cd .. && python3 -m pytest ./skraggle/tests/unit/ --disable-warnings

integration-tests:
	cd .. && python3 -m pytest ./skraggle/tests/integration/ --disable-warnings

all-tests:
	cd .. && python3 -m pytest --disable-warnings

# INITIALIZE MODEL-DB SYNC
db-init:
	cd .. && flask db init -d skraggle/migrations

# RUN MIGRATIONS
migrate:
	cd .. && flask db migrate -d skraggle/migrations

# RUN DB UPGRADE
db-upgrade:
	cd .. && flask db upgrade -d skraggle/migrations

test-auth:
	cd .. && python3 -m pytest ./skraggle/tests/integration/ --disable-warnings -k 'test_admin_auth'