cd src && \
export FLASK_APP=main.py && \
flask db upgrade && \
flask create_sudo $ADMIN_NAME $ADMIN_MAIL $ADMIN_PSWD && \
flask create_tables && \
python3 wsgi.py