FROM python:3.7-slim
RUN pip install flask
RUN pip install werkzeug
RUN pip install bcrypt
RUN pip install  pymysql
RUN pip install flask_sqlalchemy
WORKDIR /myapp1 
COPY main.py config.json /myapp1/
COPY static/assets/img/* /myapp1/static/assets/img/
COPY static/assets/favicon.ico /myapp1/static/assets/
COPY static/css/* /myapp1/static/css/
COPY static/js/* /myapp1/static/js/
COPY templates/* /myapp1/templates/
CMD ["python", "/myapp1/main.py"] 


