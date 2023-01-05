export $(grep -v '^#' .env | xargs)
cd new_skraggle
export FLASK_APP=./main.py
pip install email-validator
python3 -m pytest ./src/tests/ --disable-warnings