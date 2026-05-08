FROM python:3.11.14-alpine3.23
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY ./templates ./templates
EXPOSE 8000

RUN adduser -D app_user
USER app_user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
