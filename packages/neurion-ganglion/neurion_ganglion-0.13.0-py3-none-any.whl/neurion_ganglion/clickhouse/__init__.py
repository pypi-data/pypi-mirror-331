import os
from sqlalchemy import create_engine, MetaData
from clickhouse_sqlalchemy import (
    make_session, get_declarative_base
)

# Connection URL for ClickHouse (change it as necessary)
def engine():
    url=os.getenv("CLICKHOUSE_DATABASE_URL")
    return create_engine(url)

def session():
    return make_session(engine())


Base = get_declarative_base(metadata=MetaData())
