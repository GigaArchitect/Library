FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt update && apt install -y pkg-config default-libmysqlclient-dev gcc

RUN pip install -r requirements.txt --no-cache-dir

RUN mv library/settings.py library/settings.py.dev && mv library/settings.py.docker library/settings.py

RUN python manage.py makemigrations && python manage.py migrate

EXPOSE 8080

CMD python manage.py runserver 0.0.0.0:8080
