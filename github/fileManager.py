import os
import json
from typing import List

class FileManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        os.makedirs(self.base_dir, exist_ok=True)

    def get_next_file_number(self) -> int:
        return len([
            name for name in os.listdir(self.base_dir)
            if os.path.isfile(os.path.join(self.base_dir, name))
        ])

    def save_results(self, results: List[str], file_name: str):
        path = os.path.join(self.base_dir, file_name)
        with open(path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Saved results to {file_name}")
