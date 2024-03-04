# Build Stage
FROM python:3.8-alpine as builder

ENV DEBIAN_FRONTEND noninteractive

# Install necessary build dependencies
RUN apk update && apk add --no-cache \
    curl \
    gcc \
    g++ \
    gnupg \
    unixodbc-dev

# Install Microsoft SQL Server tools
ENV ACCEPT_EULA=Y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apk add --no-cache --virtual .build-deps gnupg \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apk/repositories \
    && apk add --no-cache --allow-unauthenticated \
        msodbcsql18 \
        mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.ashrc \
    && apk del .build-deps

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary build dependencies
RUN apk del \
    curl \
    gcc \
    g++ \
    gnupg \
    unixodbc-dev

# Runtime Stage
FROM python:3.8-alpine

COPY --from=builder /app /app

WORKDIR /app

ENV FLASK_APP=main.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
