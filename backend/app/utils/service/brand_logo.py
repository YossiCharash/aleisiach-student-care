import base64
from functools import lru_cache
from pathlib import Path


class BrandLogo:
    @staticmethod
    @lru_cache(maxsize=8)
    def data_uri(path: str) -> str:
        file = Path(path)
        if not file.is_file():
            return ""
        encoded = base64.b64encode(file.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
