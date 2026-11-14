"""configuracion global: consul apagado en los tests"""

import os

os.environ["CONSUL_ENABLED"] = "false"
os.environ.setdefault("MAX_PDF_SIZE_MB", "1")
