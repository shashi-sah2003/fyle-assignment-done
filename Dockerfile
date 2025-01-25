FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn && pip install setuptools 

COPY . .

ENV FLASK_APP=core/server.py
RUN flask db upgrade -d core/migrations/

EXPOSE 7755

COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["bash", "/app/run.sh"]