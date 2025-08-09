import json
import urllib.parse
from typing import Dict, List, Union

def generate_vless_urls(xray_config: Dict, server_name: str) -> List[str]:
    vless_urls = []
    
    # Проверяем наличие секции inbounds
    if not isinstance(xray_config.get('inbounds'), list):
        raise ValueError("Invalid Xray config: missing or invalid 'inbounds' section")
    
    for inbound in xray_config['inbounds']:
        # Проверяем что это VLESS инбаунд
        if inbound.get('protocol') != 'vless':
            continue
            
        # Базовые параметры инбаунда
        port = inbound.get('port')
        stream_settings = inbound.get('streamSettings', {})
        reality_settings = stream_settings.get('realitySettings', {})
        
        # Проверяем обязательные параметры
        if not port or not stream_settings:
            continue
            
        # Получаем список клиентов
        clients = inbound.get('settings', {}).get('clients', [])
        if not isinstance(clients, list):
            continue
            
        for client in clients:
            if not isinstance(client, dict):
                continue
                
            # Базовые параметры клиента
            uuid = client.get('id')
            email = client.get('email', '')
            flow = client.get('flow', '')
            
            if not uuid:
                continue
                
            # Формируем базовый URL
            base_url = f"vless://{uuid}@{server_name}:{port}"
            
            # Параметры запроса
            params = {
                'type': stream_settings.get('network', 'tcp'),
                'security': stream_settings.get('security', 'none'),
                'flow': flow
            }
            
            # Параметры Reality
            if reality_settings:
                params.update({
                    'sni': reality_settings.get('serverNames', [''])[0],
                    'pbk': reality_settings.get('publicKey'),
                    'sid': reality_settings.get('shortIds', [''])[0],
                    'fp': reality_settings.get('fingerprint', 'chrome')
                })
            
            # Параметры транспорта
            if stream_settings.get('network') == 'grpc':
                params['serviceName'] = stream_settings.get('grpcSettings', {}).get('serviceName')
            
            # Удаляем пустые параметры
            params = {k: v for k, v in params.items() if v}
            
            # Кодируем параметры URL
            query = urllib.parse.urlencode(params)
            
            # Формируем полный URL
            full_url = f"{base_url}?{query}#{urllib.parse.quote(email)}" if email else f"{base_url}?{query}"
            vless_urls.append(full_url)
    
    return vless_urls

def xray_config_to_vless(xray_config: Union[Dict, str]) -> List[str]:
    if isinstance(xray_config, str):
        try:
            xray_config = json.loads(xray_config)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON config") from e
    
    if not isinstance(xray_config, dict):
        raise ValueError("Config must be a dictionary or JSON string")
    
    return generate_vless_urls(xray_config)