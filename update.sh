#!/bin/bash

/usr/bin/docker run -v \
/usr/local/etc/xray/config.json:/app/config.json -v \
/usr/local/etc/xray/keycloak-sync/users:/app/users -v \
/usr/local/etc/xray/keycloak-sync/template.j2:/app/template.j2 \
--env-file /usr/local/etc/xray/keycloak-sync/.env \
-it --rm sudoroot/xray-keycloak:v0.0.1

FILE="/usr/local/etc/xray/config.json"

if [ ! -f "$FILE" ]; then
  echo "Файл не существует"
  exit 1
fi

# Время последней модификации файла (в секундах с начала эпохи UNIX)
file_mod_time=$(stat -c %Y "$FILE")

# Время ровно один час назад
one_hour_ago=$(date -d "1 hour ago" +%s)

if [ "$file_mod_time" -ge "$one_hour_ago" ]; then
  echo "Файл был создан или изменён за последний час"
  systemctl restart xray
else
  echo "Файл не изменяли в течение последнего часа"
fi