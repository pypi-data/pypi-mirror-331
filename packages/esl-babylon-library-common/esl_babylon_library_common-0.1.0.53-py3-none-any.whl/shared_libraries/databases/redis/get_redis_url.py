from shared_libraries.core.config import app_common_config


def get_redis_url(is_remote: bool,
                  redis_db: int = 0, add_certificate_reqs_param=False) -> str:
    ssl_cert_option = 'CERT_NONE'  # change this to 'CERT_REQUIRED' or 'CERT_OPTIONAL' CERT_NONE
    if is_remote:
        redis_url = (
            f"redis://:"
            f"{app_common_config.remote_redis_password}@"
            f"{app_common_config.remote_redis_host}:"
            f"{app_common_config.remote_redis_port}/"
            f"{redis_db}"
        )
        if add_certificate_reqs_param:
            redis_url += f"?ssl_cert_reqs={ssl_cert_option}"
    else:
        redis_url = (
            f"redis://:"
            f"{app_common_config.redis_password}@"
            f"{app_common_config.redis_host}:"
            f"{app_common_config.redis_port}/"
            f"{redis_db}"
        )

    return redis_url
