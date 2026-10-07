from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    debug: bool = False
    environment: str = "development"
    tracing_enabled: bool = False
    tracing_exporter: Literal["console", "otlp"] = "console"
    tracing_otlp_endpoint: str = "http://portfolio-otel:4318/v1/traces"
    tracing_sample_ratio: float = Field(default=0.1, ge=0, le=1)

    project_name: str
    api_version: str

    admin_username: str
    admin_password: str

    # Local development serves files from app/static. In production, the same
    # database paths are translated to CloudFront URLs instead.
    cloudfront_domain: str | None = None
    s3_bucket: str | None = None
    aws_region: str = "us-east-2"
    serve_local_static_files: bool | None = None
    # Comma-separated ALB subnet CIDRs. Empty means forwarded headers are ignored.
    security_trusted_proxy_cidrs: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def trusted_proxy_cidrs(self) -> tuple[str, ...]:
        return tuple(value.strip() for value in self.security_trusted_proxy_cidrs.split(",")
                     if value.strip())

    @property
    def should_serve_local_static_files(self) -> bool:
        if self.serve_local_static_files is not None:
            return self.serve_local_static_files
        return self.environment != "production"

    def asset_url(self, path_or_url: str) -> str:
        """Return a CloudFront URL for a local portfolio asset when configured."""
        if not self.cloudfront_domain or not path_or_url.startswith("/static/"):
            return path_or_url

        base_url = self.cloudfront_domain.rstrip("/")
        object_key = path_or_url.removeprefix("/static/")
        return f"{base_url}/{object_key}"


settings = Settings()
