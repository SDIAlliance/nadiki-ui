FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ /usr/src/app

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["nadiki_ui:app", "-b", "0.0.0.0"]
