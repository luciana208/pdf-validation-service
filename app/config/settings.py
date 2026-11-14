"""configuracion del servicio leida de variables de entorno (12-factor iii)"""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # identidad del servicio
    service_name: str = Field("pdf-validation-service")
    service_version: str = Field("1.0.0")
    log_level: str = Field("INFO")

    # el puerto es el mismo que usa granian, asi hay una sola variable
    port: int = Field(8000, validation_alias=AliasChoices("GRANIAN_PORT", "PORT"))

    # reglas de validacion
    max_pdf_size_mb: int = Field(10)

    # registro en consul
    consul_enabled: bool = Field(False)
    consul_url: str = Field("http://consul:8500")
    consul_token: str = Field("")
    service_address: str = Field("")
    health_check_interval: str = Field("10s")

    # ruteo en traefik (los tags viajan en el registro de consul)
    router_name: str = Field("validation")
    public_host: str = Field("")
    internal_host: str = Field("validation.internal")
    circuit_breaker_expression: str = Field(
        "NetworkErrorRatio() > 0.5 || ResponseCodeRatio(500, 600, 0, 600) > 0.25"
    )
    retry_attempts: int = Field(3)
    retry_initial_interval: str = Field("100ms")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @property
    def max_pdf_size_bytes(self) -> int:
        return self.max_pdf_size_mb * 1024 * 1024


settings = Settings()
