FROM python:3.12-slim

ENV APP_HOME=/app 

WORKDIR /app

COPY . /app

RUN pip install --no-cache -r requirements.txt
RUN pip install aiohttp aiopath

RUN chmod +x run_servers.sh

EXPOSE 8000/tcp 8082

VOLUME ["$APP_HOME/logs"]

ENTRYPOINT [ "/bin/sh", "run_servers.sh"]