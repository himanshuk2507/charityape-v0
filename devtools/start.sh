cd new_skraggle
export FLASK_APP=./main.py

echo "\n\n************* RUNNING MIGRATIONS *************\n\n"
echo "\n\n************* UPDATING DATABASE *************\n\n"

pip install email-validator
celery --app run.celery worker --loglevel=info --detach
flask db upgrade
flask cli seed
