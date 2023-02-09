FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./scripts /scripts

WORKDIR /app
EXPOSE 8000

RUN apk add --update qt5-qtbase-dev wkhtmltopdf --no-cache \
    --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted

RUN apk --no-cache add msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f

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
RUN chmod -R 0755 /vol
RUN chmod -R +x /scripts
#RUN chown -R app:app /app/locale

ENV PATH="/scripts:/py/bin:$PATH"
ENV XDG_RUNTIME_DIR="/tmp/runtime-app"

USER app

CMD ["run.sh"]