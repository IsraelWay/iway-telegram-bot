#!/bin/bash
docker-compose build crm
docker-compose push crm

ssh iway@server.israelway.ru << EOF
cd crm/iway-telegram-bot/ || exit

docker-compose pull
docker-compose up -d --force-recreate crm
EOF