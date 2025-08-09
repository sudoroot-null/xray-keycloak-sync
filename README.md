# Порядок запуска
- Создаем env файл settings.env
### Параметры settings.env
#### Конфигурация Keycloak
KEYCLOAK_URL="https://keycloack.my"
REALM="my-realm"
CLIENT_ID="my-cliend-id"
CLIENT_SECRET="supersecret"
XRAY_CONFIG_PATH="config.json"
EXTERNAL_DOMAIN_NAME="mysite.local"
#### Группы для разделения доступа в keycloak
FULL_ACCESS_GROUP="vpn_full_access"
RESTRICTED_GROUP="vpn_internet_only"

### Поправьте шаблон конфигурационного файла xray под себя
```
vim template.j2
```

### Сборка
Docker образ надо предварительно собрать

### Запуск
- При запуске монтируем конфигурационный файл xray, чтобы скрипт мог его обновить.
- И монтируем пока еще несуществующий файл users, в который будут выгружены строки для настройки клиентских подключений.
```
docker run users-sync --image xray-sync --rm \
--env-file settings.env \
-v ./config.json:/usr/local/etc/xray/config.json \
-v ./users:/usr/local/etc/xray/users \
-v ./template.j2:/usr/local/etc/xray/template.j2
```