import hashlib

from app.business.domain.checksum_calculator import calculate_checksum


def test_devuelve_sha256_hexadecimal():
    assert calculate_checksum(b"abc") == hashlib.sha256(b"abc").hexdigest()


def test_mismo_contenido_mismo_checksum():
    assert calculate_checksum(b"pdf") == calculate_checksum(b"pdf")


def test_distinto_contenido_distinto_checksum():
    assert calculate_checksum(b"a") != calculate_checksum(b"b")
