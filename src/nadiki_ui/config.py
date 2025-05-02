import os

def get_database_url():
    database_host = os.environ.get("DATABASE_HOST")
    database_user = os.environ.get("DATABASE_USER")
    database_password = os.environ.get("DATABASE_PASSWORD")
    return f"mysql+pymysql://{database_user}:{database_password}@{database_host}/nadiki_ui?charset=utf8mb4"

def get_influxdb_endpoint_url():
    return os.environ.get("INFLUXDB_ENDPOINT_URL")

def get_influxdb_org():
    return os.environ.get("INFLUXDB_ORG")

def get_influxdb_admin_token():
    return os.environ.get("INFLUXDB_ADMIN_TOKEN")
