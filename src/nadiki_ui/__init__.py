import datetime

from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import select, delete, insert

from nadiki_ui.database import database_engine, snapshots_table
from nadiki_ui.snapshot_state_enum import SnapshotStateEnum
from nadiki_ui.influxdb import influxdb_client
from nadiki_ui.create_snapshot_thread import CreateSnapshotThread

app = Flask(__name__)

@app.route("/")
def homepage():
    with database_engine().connect() as conn:
        result = conn.execute(select(snapshots_table()))
    bucket_names = [x["name"] for x in influxdb_client().buckets_api().find_buckets().to_dict()["buckets"] if x["name"].startswith("FACILITY")]
    
    date_from = datetime.date.today() - datetime.timedelta(days=1)
    date_until = datetime.date.today()

    return render_template("index.html", snapshots=result, bucket_names=bucket_names, date_from=date_from, date_until=date_until, delete_url=url_for("delete_snapshot"), insert_url=url_for("insert_snapshot"))

@app.route("/delete")
def delete_snapshot():
    with database_engine().connect() as conn:
        bucket = influxdb_client().buckets_api().find_bucket_by_name(f"SNAPSHOT-{request.args.get('id')}")
        influxdb_client().buckets_api().delete_bucket(bucket.id)
        conn.execute(delete(snapshots_table()).where(snapshots_table().c.id == request.args.get('id')))
        conn.commit()
    return redirect(url_for("homepage"))

@app.route("/insert", methods=["POST"])
def insert_snapshot():
    with database_engine().connect() as conn:
        newid = conn.execute(insert(snapshots_table()).values(
            {
                    'name': request.form['name'],
                    'facility_id': request.form['facility_id'],
                    'time_from': datetime.datetime.strptime(f"{request.form['date_from']} {request.form['time_from']}", '%Y-%m-%d %H:%M:%S'),
                    'time_until': datetime.datetime.strptime(f"{request.form['date_until']} {request.form['time_until']}", '%Y-%m-%d %H:%M:%S'),
                    'state': SnapshotStateEnum.NEW # "new"
            }
        )).inserted_primary_key[0]
        conn.commit()
    
    # create the snapshot asynchronously in the background because it might take time
    thread = CreateSnapshotThread(newid)
    return redirect(url_for("homepage"))

