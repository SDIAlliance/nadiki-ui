import os
import influxdb_client

influxdb_client = influxdb_client.InfluxDBClient(
    url         = os.environ.get("INFLUXDB_ENDPOINT_URL"),
    token       = os.environ.get("INFLUXDB_ADMIN_TOKEN"),
    org         = os.environ.get("INFLUXDB_ORG"),
    verify_ssl  = False # required to use the service discovery to connect internally
)
