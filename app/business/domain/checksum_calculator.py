import hashlib


def calculate_checksum(file_bytes: bytes) -> str:
    # sha-256 del contenido en hexadecimal (64 caracteres)
    return hashlib.sha256(file_bytes).hexdigest()
