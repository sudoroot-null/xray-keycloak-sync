import json
from typing import Optional

def read_current_config(path: str) -> Optional[dict]:
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def compare_configs(new_config: str, current_config: Optional[dict]) -> bool:
    if current_config is None:
        return True
    
    try:
        new_config_dict = json.loads(new_config)
        return new_config_dict != current_config
    except json.JSONDecodeError:
        return True

def save_config_if_changed(new_config: str, path: str) -> bool:
    current_config = read_current_config(path)
    
    if compare_configs(new_config, current_config):
        # Создаем резервную копию текущего конфига
        if current_config is not None:
            backup_path = f"{path}.bak"
            with open(backup_path, 'w') as f:
                json.dump(current_config, f, indent=2)
            print(f"Created backup of current config at {backup_path}")
        
        # Сохраняем новый конфиг
        with open(path, 'w') as f:
            f.write(new_config)
        print(f"Config updated at {path}")
        return True
    else:
        print("Config unchanged, no update needed")
        return False