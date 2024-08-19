ROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --disable-pip-version-check -r requirements.txt
# RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y iputils-ping 

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . .

# RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate

CMD ["gunicorn", "subnet_ip_app.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["celery", "-A", "subnet_ip_app", "worker", "-l", "info", "-Q", "queue1"]
