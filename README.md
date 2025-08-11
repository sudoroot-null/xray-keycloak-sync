# Что это и зачем?
Этот небольшой проект был написан с целью автоматизации синхронизации пользователей из keycloak в Xray с возможностью группировки пользователей и разграничения доступа.

### Сборка
Docker образ надо предварительно собрать или взять готовый из docker hub https://hub.docker.com/r/sudoroot/xray-keycloak


### Подготовка
- Создаем каталог, в который положим нужные файлы
- При запуске монтируем файлы внутрь докер контейнера
```
mkdir /usr/local/etc/xray/keycloak-sync
cd /usr/local/etc/xray/keycloak-sync
touch users config.json template.j2 .env
```

### Параметры .env файла
```
KEYCLOAK_URL="https://keycloack.my"
REALM="my-realm"
CLIENT_ID="my-cliend-id"
CLIENT_SECRET="supersecret"
XRAY_CONFIG_PATH="config.json"
EXTERNAL_DOMAIN_NAME="mysite.local"
#### Группы для разделения доступа в keycloak
FULL_ACCESS_GROUP="vpn_full_access"
RESTRICTED_GROUP="vpn_internet_only"
```

### template.j2
Посмотрите файл template_example.j2 на основании него можете сделать свой.

### Запуск
```
/usr/bin/docker run -v \
/usr/local/etc/xray/config.json:/app/config.json -v \
/usr/local/etc/xray/keycloak-sync/users:/app/users -v \
/usr/local/etc/xray/keycloak-sync/template.j2:/app/template.j2 \
--env-file /usr/local/etc/xray/keycloak-sync/.env \
-it --rm sudoroot/xray-keycloak:v0.0.1
```

### Результат
После работы скрипта мы получаем обновленный config.json по пути /usr/local/etc/xray/config.json
А так же заполненный файл /usr/local/etc/xray/keycloak-sync/users, в котором хранятся строки для подключения пользователей.

### И что мне руками это запускать?
В репозитории есть update.sh, который вы можете добавить в cron, и в зависимости от того был ли обновлен файл config.json он будет перезапускать сервис xray.