# inspired by https://stackoverflow.com/questions/40989671/background-tasks-in-flask

import os
import threading
from sqlalchemy import select, update

from nadiki_ui.database import database_engine, snapshots_table
from nadiki_ui.influxdb import influxdb_client

class CreateSnapshotThread:

    def __init__(self, snapshot_id):
        thread = threading.Thread(target=self.run, args=(snapshot_id,))
        thread.daemon = True                       # Daemonize thread
        thread.start()                             # Start the execution

    def run(self, snapshot_id):
        with database_engine().connect() as conn:
            result = conn.execute(select(snapshots_table()).where(snapshots_table().c.id == snapshot_id))
            snapshot = next(result)
            bucket = influxdb_client().buckets_api().create_bucket(
                bucket_name     = f"SNAPSHOT-{snapshot.id}",
                org             = os.environ.get("INFLUXDB_ORG"),
            )
            conn.execute(update(snapshots_table()).where(snapshots_table().c.id == snapshot_id).values({"state": "pending" }))
            conn.commit();
            query = f"""from(bucket: "{snapshot.facility_id}")
        |> range(start: {snapshot.time_from.isoformat()}Z, stop: {snapshot.time_until.isoformat()}Z)
        |> to(bucket: "SNAPSHOT-{snapshot.id}")"""
            #print(query)
            influxdb_client().query_api().query(query=query)
            conn.execute(update(snapshots_table()).where(snapshots_table().c.id == snapshot_id).values({"state": "ready" }))
            conn.commit();
