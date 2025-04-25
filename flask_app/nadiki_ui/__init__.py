import os
import boto3
import json

from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import create_engine, text, MetaData, Table, Column, Sequence, Integer, String, select, delete, insert

from nadiki_ui.database import engine, snapshots
from nadiki_ui.snapshot_state_enum import SnapshotStateEnum
from nadiki_ui.influxdb import influxdb_client

app = Flask(__name__)

sqs = boto3.client('sqs')
buckets_api = influxdb_client.buckets_api()

@app.route("/")
def homepage():
    with engine.connect() as conn:
        result = conn.execute(select(snapshots))
    bucket_names = [x["name"] for x in buckets_api.find_buckets().to_dict()["buckets"]]
    
    return render_template("index.html", snapshots=result, bucket_names=bucket_names, delete_url=url_for("delete_snapshot"), insert_url=url_for("insert_snapshot"))

@app.route("/delete")
def delete_snapshot():
    with engine.connect() as conn:
        bucket = buckets_api.find_bucket_by_name(f"SNAPSHOT-{request.args.get('id')}")
        buckets_api.delete_bucket(bucket.id)
        conn.execute(delete(snapshots).where(snapshots.c.id == request.args.get('id')))
        conn.commit()
    return redirect(url_for("homepage"))

@app.route("/insert", methods=["POST"])
def insert_snapshot():
    with engine.connect() as conn:
        newid = conn.execute(insert(snapshots).values(
            {
                    'name': request.form['name'],
                    'facility_id': request.form['facility_id'],
                    'time_from': datetime.strptime(f"{request.form['date_from']} {request.form['time_from']}", '%Y-%m-%d %H:%M:%S'),
                    'time_until': datetime.strptime(f"{request.form['date_until']} {request.form['time_until']}", '%Y-%m-%d %H:%M:%S'),
                    'state': "new"
            }
        )).inserted_primary_key[0]
        conn.commit()
    
    sqs.send_message(
        QueueUrl=os.environ.get("SQS_QUEUE_URL"),
        MessageBody=json.dumps({
            "snapshot_id": newid
        })
    )
    return redirect(url_for("homepage"))

