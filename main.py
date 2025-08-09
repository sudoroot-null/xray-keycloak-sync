import requests
from jinja2 import Template
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
from xray_vless_url_generator import generate_vless_urls
from config_process import save_config_if_changed, read_current_config, compare_configs
load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FULL_ACCESS_GROUP = os.getenv("FULL_ACCESS_GROUP")
RESTRICTED_GROUP = os.getenv("RESTRICTED_GROUP")
XRAY_CONFIG_PATH = os.getenv("XRAY_CONFIG_PATH")
EXTERNAL_DOMAIN_NAME = os.getenv("EXTERNAL_DOMAIN_NAME")

with open("template.j2", "r") as f:
  XRAY_CONFIG_TEMPLATE = f.read()
  if XRAY_CONFIG_TEMPLATE == "":
    raise Exception("XRAY_CONFIG_TEMPLATE is empty")

def get_keycloak_token() -> str:
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, data=payload, verify=False)
    response.raise_for_status()
    return response.json()["access_token"]

def get_users_with_groups(token: str) -> Dict[str, List[Dict]]:
    users_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем всех пользователей
    users = requests.get(users_url, headers=headers, verify=False).json()
    
    # Для каждого пользователя получаем группы
    result = {"full_access": [], "restricted": []}
    for user in users:
        groups_url = f"{users_url}/{user['id']}/groups"
        groups = requests.get(groups_url, headers=headers, verify=False).json()
        
        group_names = [group['name'] for group in groups]
        
        if FULL_ACCESS_GROUP in group_names:
            result["full_access"].append({
                "uuid": user.get("attributes", {}).get("vless_uuid", [""])[0] or user["id"],
                "email": user.get("email", ""),
                "username": user.get("username", "")
            })
        elif RESTRICTED_GROUP in group_names:
            result["restricted"].append({
                "uuid": user.get("attributes", {}).get("vless_uuid", [""])[0] or user["id"],
                "email": user.get("email", ""),
                "username": user.get("username", "")
            })
    
    return result

def generate_xray_config(users: Dict[str, List[Dict]]) -> str:
    template = Template(XRAY_CONFIG_TEMPLATE)
    return template.render(
        full_access_users=users["full_access"],
        restricted_users=users["restricted"]
    )


def main():
    try:
        # 1. Аутентификация в Keycloak
        token = get_keycloak_token()
        
        # 2. Получение пользователей с группами
        users = get_users_with_groups(token)
        print(f"Found {len(users['full_access'])} full access users")
        print(f"Found {len(users['restricted'])} restricted users")
        
        if len(users['full_access']) == 0 and len(users['restricted']) == 0:
            raise Exception("No users found")

        # 3. Генерация конфигурации
        xray_config = generate_xray_config(users)
        
        with open("users", "w") as f:
          for line in generate_vless_urls(json.loads(xray_config), EXTERNAL_DOMAIN_NAME):
            f.write(line + "\n")

        # 4. Сохранение в файл только при изменениях
        config_changed = save_config_if_changed(xray_config, XRAY_CONFIG_PATH)
        
        if config_changed:
            print("Configuration was updated")
        else:
            print("Configuration remains unchanged")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())