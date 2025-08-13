from __future__ import annotations
import json
from pathlib import Path
from typing import List
from django.conf import settings
from filelock import FileLock

DB_DIR = Path(settings.BASE_DIR) / 'db'
DB_DIR.mkdir(parents=True, exist_ok=True)

class JSONTable:
    def __init__(self, filename: str):
        self.path = DB_DIR / filename
        self.lock = FileLock(str(self.path) + '.lock')
        if not self.path.exists():
            self.path.write_text('[]', encoding='utf-8')

    def read(self) -> List[dict]:
        with self.lock:
            txt = self.path.read_text(encoding='utf-8')
            try:
                return json.loads(txt)
            except json.JSONDecodeError:
                return []

    def write(self, rows: List[dict]) -> None:
        with self.lock:
            self.path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8'
            )

    def get_by_id(self, _id: str, *, id_field: str = 'id') -> dict | None:
        for r in self.read():
            if r.get(id_field) == _id:
                return r
        return None

    def upsert(self, row: dict, *, id_field: str = 'id') -> None:
        rows = self.read()
        for i, r in enumerate(rows):
            if r.get(id_field) == row.get(id_field):
                rows[i] = row
                self.write(rows)
                return
        rows.append(row)
        self.write(rows)
