from sqlalchemy import create_engine, MetaData, Table, Column, Sequence, Integer, String, DateTime, Enum

from nadiki_ui.snapshot_state_enum import SnapshotStateEnum
from nadiki_ui.config import get_database_url

engine = None
snapshots = None

def database_engine():
    global engine
    if engine == None:
        engine = create_engine(get_database_url(), pool_pre_ping=True)

    return engine

def snapshots_table():
    global snapshots

    if snapshots == None:
        meta = MetaData()
        meta.reflect(database_engine())
        snapshots = Table("snapshots", meta,
            Column("id", Integer, Sequence("id_seq", start=1), primary_key=True),
            Column("name", String(50)),
            Column("facility_id", String(50)),
            Column("time_from", DateTime(255)),
            Column("time_until", DateTime(255)),
            Column("state", Enum(SnapshotStateEnum)),
            extend_existing=True
        )
        try:
            meta.create_all(engine)
        except:
            #snapshots = Table("snapshots", meta, autoload_with=engine)
            pass

    return snapshots
