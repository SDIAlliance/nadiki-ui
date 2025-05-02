import os
import requests

def _get_secret_or_default(secret_name, default):
    if os.environ.get('AWS_SESSION_TOKEN') != None:
        headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
        secrets_extension_endpoint = f"http://localhost:2773/secretsmanager/get?secretId="
        r = requests.get(secrets_extension_endpoint+secret_name, headers=headers)
        return  r.text
    else:
        return default

def get_database_url():
    database_host = os.environ.get("DATABASE_HOST")
    database_user = os.environ.get("DATABASE_USER")
    database_password = _get_secret_or_default("nadiki-prod-mariadb-root-password", os.environ.get("DATABASE_PASSWORD"))
    return f"mysql+pymysql://{database_user}:{database_password}@{database_host}/nadiki_ui?charset=utf8mb4"

def get_influxdb_endpoint_url():
    return os.environ.get("INFLUXDB_ENDPOINT_URL")

def get_influxdb_org():
    return os.environ.get("INFLUXDB_ORG")

def get_influxdb_admin_token():
    return _get_secret_or_default("nadiki-prod-influxdb-admin-token", os.environ.get("INFLUXDB_ADMIN_TOKEN"))
