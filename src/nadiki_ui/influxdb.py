import influxdb_client as infcl

from nadiki_ui.config import get_influxdb_endpoint_url, get_influxdb_admin_token, get_influxdb_org

def influxdb_client(): 
    return infcl.InfluxDBClient(
        url         = get_influxdb_endpoint_url(),
        token       = get_influxdb_admin_token(),
        org         = get_influxdb_org(),
        verify_ssl  = False # required to use the service discovery to connect internally
    )
