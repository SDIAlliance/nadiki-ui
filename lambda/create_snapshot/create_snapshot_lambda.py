import sys
import os
import json

from sqlalchemy import select, update

from nadiki_ui.influxdb import influxdb_client
from nadiki_ui.database import engine, snapshots
from nadiki_ui.snapshot_state_enum import SnapshotStateEnum

print(sys.path)
buckets_api = influxdb_client.buckets_api()
query_api = influxdb_client.query_api()

def lambda_handler(event, context):
    msg = json.loads(event["Records"][0]["body"])
    #print(buckets_api.find_buckets())
    with engine.connect() as conn:
        result = conn.execute(select(snapshots).where(snapshots.c.id == msg["snapshot_id"]))
        snapshot = next(result)
        bucket = buckets_api.create_bucket(
            bucket_name     = f"SNAPSHOT-{snapshot.id}",
            org             = os.environ.get("INFLUXDB_ORG"),
        )
        conn.execute(update(snapshots).where(snapshots.c.id == msg["snapshot_id"]).values({"state": "pending" }))
        conn.commit();
        query = f"""from(bucket: "{snapshot.facility_id}")
    |> range(start: {snapshot.time_from.isoformat()}Z, stop: {snapshot.time_until.isoformat()}Z)
    |> to(bucket: "SNAPSHOT-{snapshot.id}")"""
        print(query)
        query_api.query(query=query)
        conn.execute(update(snapshots).where(snapshots.c.id == msg["snapshot_id"]).values({"state": "ready" }))
        conn.commit();

if __name__ == "__main__":
    lambda_handler({
        "Records": [
            {
                "messageId": "abec53ae-9e4a-46ad-961b-dc244c8632b5",
                "receiptHandle": "AQEBPzPa4ifARYTlHSz3RUfr4F0gwrPEtsZjSYn6P1Yo39QfFhvdgQpteW7is95/zxtHHRrwLfvG+qyZ1Xmij0giVfJOqoPLi+fakpE93AczcRcmDerv9lprJHtOIvLJbml437fc6PrjHorC/7THeqPYrZoRtck34IO2Tfm6Bo8XLPcJ/PiuaWYjez4n61CbwtHFK/ARbqJnn1FeMHsMuRoFRxSw67JuYpJ+RlQazJq5QyJQqzaW9NPVszvz4XzWuaTndSE5HJa7Dzo4n8FNvxDdNhppuWyGgh4S4RZwpgmztH2sbwPUFrs1Q0snvCS+jpR1UdVzWoCgdDRLH1sSNDxOw3BOr0LMOkC4vqAnNPIlwjHFmfQg/cpAnfsXzkJSwjlHlI7hLkQDceOMbZa20jZfM8LIABMxOBJlJ/aiSEp6t4Y=",
                "body": "{\"snapshot_id\": 3}",
                "attributes": {
                    "ApproximateReceiveCount": "3",
                    "SentTimestamp": "1745570763939",
                    "SenderId": "AROAYTVLG7RHHRPBW24QR:danielboesswetter",
                    "ApproximateFirstReceiveTimestamp": "1745570772872"
                },
                "messageAttributes": {},
                "md5OfBody": "7b39a5bcae7676f9749278ae757edc59",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:eu-central-1:591990815822:nadiki-snapshot-creation",
                "awsRegion": "eu-central-1"
            }
        ]
    }, None)
