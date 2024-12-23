FROM python:3.12-slim

WORKDIR /src/

COPY . .

RUN apt update

RUN apt install -y pkg-config default-libmysqlclient-dev gcc

RUN pip install -r requirements.txt

EXPOSE 8080

RUN cd library && mv settings.py.docker settings.py

RUN python manage.py makemigrations

RUN python manage.py migrate

CMD python manage.py runserver 8080

