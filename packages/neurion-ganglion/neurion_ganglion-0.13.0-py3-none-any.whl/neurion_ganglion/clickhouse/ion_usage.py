from datetime import date
from sqlalchemy import  Column
from clickhouse_sqlalchemy import (
    Table,  types, engines
)

from neurion_ganglion.clickhouse import Base, session


# Define the IonUsage table for ClickHouse
class IonUsage(Base):
    __tablename__ = "ion_usage"

    # Define the columns and their types using clickhouse_sqlalchemy.types
    ion_address = Column(types.String, primary_key=True)   # Address of the Ion
    user_address = Column(types.String, primary_key=True)  # Address of the user
    num_of_calls = Column(types.Int32)               # Number of calls
    created_at = Column(types.DateTime64, default="now()")  # DateTime column with a default value

    # Define the storage engine (using MergeTree for this example) and set the primary key in __table_args__
    __table_args__ = (
        engines.MergeTree(
            "created_at",  # Sorting key for MergeTree engine
            order_by=["created_at"],  # Sorting by created_at column
        ),
    )

    @classmethod
    def table(cls) -> Table:
        return cls.__table__

class IonUsageDAO:
    """Data Access Object for IonUsage model."""

    @staticmethod
    def increment_usage(ion_address: str, user_address: str):
        # Check if the row exists
        result = session().execute(
            IonUsage.table().select().filter_by(ion_address=ion_address, user_address=user_address)
        )
        entry = result.first()

        # If the entry exists, perform an UPDATE
        if entry:
            session().execute(
                IonUsage.table().update()
                .where(IonUsage.table().c.ion_address == ion_address)
                .where(IonUsage.table().c.user_address == user_address)
                .values(num_of_calls=entry.num_of_calls + 1)
            )
        # If the entry doesn't exist, perform an INSERT
        else:
            session().execute(
                IonUsage.table().insert(),
                {"ion_address": ion_address, "user_address": user_address, "num_of_calls": 1,
                 "created_at": date.today()}
            )

    @staticmethod
    def delete_usage(ion_address: str, user_address: str):
        session().execute(
            IonUsage.table().delete().where(IonUsage.table().c.ion_address == ion_address)
                .where(IonUsage.table().c.user_address == user_address)
        )

    @staticmethod
    def get_num_of_calls(ion_address: str, user_address: str):
        # Query to get the number of calls from ClickHouse
        result = session().execute(
            IonUsage.table().select().filter_by(ion_address=ion_address, user_address=user_address)
        )
        entry = result.first()
        return entry.num_of_calls if entry else None
