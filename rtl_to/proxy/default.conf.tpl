server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10G;
    }
}

server {
    listen ${LISTEN_TECH_API_PORT};

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${TECH_API_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10G;
    }
}