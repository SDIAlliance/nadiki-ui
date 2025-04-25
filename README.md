# UI for Nadiki

Allow users to list their snapshots, delete existing snapshots and create new ones.

A snapshot is described by
- bucket (equals facility ID)
- time and data range

When a snapshot is created, an entry in the database is made (with state=new). The ID
of the snapshot is then send to an SNS topic which triggering a Lambda, that creates
a bucket in InfluxDB (with unlimited retention) and copies the relevant data into it.
Finally, the state of the snapshot is set to "ready" in the database. When the user
deletes a snapshot, the bucket is removed from InfluxDB and the corresponding line
is removed from the database.

What happens when the Lambda fails and the message goes to the DLQ?
