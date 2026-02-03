FROM python:3.11.14-alpine3.23
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev \
    && pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY app.py ./
EXPOSE 8000

COPY ./templates ./templates

RUN adduser -D app_user
USER app_user

CMD ["python", "app.py"]