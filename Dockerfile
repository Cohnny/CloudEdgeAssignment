FROM python:3-alpine3.17
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 3000
ENV FLASK_APP=main.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]