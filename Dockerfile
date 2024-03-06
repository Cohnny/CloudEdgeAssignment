FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        gnupg \
        unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV ACCEPT_EULA=Y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
        msodbcsql18 \
        mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=main.py
# EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]