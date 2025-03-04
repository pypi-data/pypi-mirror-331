DOCKERFILE = """FROM python:3.11.1

WORKDIR /usr/src/app

ENV PYTHONDONTWRITENYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app

RUN python -m pip install gunicorn
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /usr/src/app
EXPOSE 8000
"""

DOCKER_COMPOSE = """version: '3.11.1'

services:
  web:
    build:
      context: .
    container_name: "web"
    restart: always
    command: bash ./entrypoint.sh
    ports:
      - 8000:8000
    env_file:
      - .env.dev
    networks:
      - my_network
    depends_on:
      - db

  db:
    image: postgres:latest
    container_name: "db"
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - my_network

networks:
  my_network:

volumes:
  media_volume:
  db_data:
"""

ENTRYPOINT = """
# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset
export DJANGO_SETTINGS_MODULE=config.settings.development

echo "Running migrations..."
# python manage.py makemigrations
# python manage.py migrate
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Running tests..."
python manage.py test
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000
"""

REQUIREMENTS = """Django"""
