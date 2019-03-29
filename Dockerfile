FROM python:3.6

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/hogwarts-bot-credentials.json
ADD requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

COPY src/ /app/

WORKDIR /app

ENTRYPOINT ["/app/main.py"]