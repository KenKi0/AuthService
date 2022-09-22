cd src && \
export FLASK_APP=main.py && \
flask db upgrade && \
flask test_data && \
python3 -m pytest tests/functional/src --full-trace