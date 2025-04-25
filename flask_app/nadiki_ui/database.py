import os
from sqlalchemy import create_engine, MetaData, Table, Column, Sequence, Integer, String, DateTime, Enum

from nadiki_ui.snapshot_state_enum import SnapshotStateEnum

engine = create_engine(os.environ.get("DATABASE_URL") or "sqlite:///data.db")

meta = MetaData()
meta.reflect(engine)
try:
    snapshots = Table("snapshots", meta,
        Column("id", Integer, Sequence("id_seq", start=1), primary_key=True),
        Column("name", String(50)),
        Column("facility_id", String(50)),
        Column("time_from", DateTime(255)),
        Column("time_until", DateTime(255)),
        Column("state", Enum(SnapshotStateEnum))
    )
    meta.create_all(engine)
except:
    snapshots = Table("snapshots", meta, autoload_with=engine)
