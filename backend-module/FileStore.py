import json
import os

class FileStorage:
    def __init__(self, filename="blockchain_data.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, filename)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Garante que o arquivo exista e repara arquivos vazios (0 bytes)."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump([], file)

    def _load_data(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _save_data(self, data):
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def create(self, record):
        data = self._load_data()
        data.append(record)
        self._save_data(data)
        return True

    def read(self, record_id=None):
        data = self._load_data()
        if record_id is not None:
            for item in data:
                if item.get("id") == record_id:
                    return item
            return None
        return data 