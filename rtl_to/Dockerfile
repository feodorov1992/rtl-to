FROM surnet/alpine-python-wkhtmltopdf:3.10.6-0.12.6-small

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./branding /branding
COPY ./scripts /scripts

WORKDIR /app
EXPOSE 8000

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-deps build-base postgresql-dev musl-dev linux-headers

RUN python -m venv /py
RUN /py/bin/pip install --upgrade pip
RUN /py/bin/pip install wheel
RUN /py/bin/pip install -r /requirements.txt

RUN apk del .tmp-deps

RUN adduser --disabled-password --no-create-home app
RUN mkdir -p /vol/web/static
RUN mkdir -p /vol/web/media
RUN chown -R app:app /vol
RUN chown -R app:app /branding
RUN chmod -R 0755 /vol
RUN chmod -R 0755 /branding
RUN chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"
ENV XDG_RUNTIME_DIR="/tmp/runtime-app"

USER app

CMD ["run.sh"]