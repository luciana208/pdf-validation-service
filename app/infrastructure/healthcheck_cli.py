"""chequeo de salud que usa el healthcheck del dockerfile (la imagen no trae curl)"""

import sys
import urllib.request

from app.config.settings import settings


def main() -> int:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{settings.port}/health", timeout=2) as response:
            return 0 if response.status == 200 else 1
    except OSError:
        return 1


if __name__ == "__main__":
    sys.exit(main())
