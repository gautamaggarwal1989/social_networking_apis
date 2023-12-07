FROM python:3.5.7

ENV PYTHONUNBUFFERED 1

WORKDIR /project_dir

RUN ls .

RUN pip install -r requirements.txt

VOLUME /project_dir

EXPOSE 8080

CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
