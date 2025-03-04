from sqlalchemy import Column
from clickhouse_sqlalchemy import (
    Table, types, engines, select
)
from datetime import date
from neurion_ganglion.clickhouse import Base, session  # Assuming your base is defined here


class PathwayUsage(Base):
    __tablename__ = "pathway_usage"

    # Define the columns and their types using clickhouse_sqlalchemy.types
    pathway_id = Column(types.Int32, primary_key=True)
    user_address = Column(types.String, primary_key=True)
    num_of_calls_settled = Column(types.Int32)
    num_of_calls_pending = Column(types.Int32)
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


class PathwayUsageDAO:
    """Data Access Object for PathwayUsage model."""

    @staticmethod
    def get_num_of_calls_pending(pathway_id: int, user_address: str):
        """
        Retrieves the number of pending calls for the given pathway_id and user_address.
        """
        # Query to get the pending calls from ClickHouse
        result = session().execute(
            PathwayUsage.table().select().filter_by(pathway_id=pathway_id, user_address=user_address)
        )
        entry = result.first()
        return entry if entry else None

    @staticmethod
    def increment_calls_pending(pathway_id: int, user_address: str):
        """
        Increases num_of_calls_pending by 1 for the given pathway_id and user_address.
        If the entry does not exist, insert a new record with num_of_calls_pending = 1.
        """
        # Check if the entry exists in ClickHouse
        result = session().execute(
            PathwayUsage.table().select().filter_by(pathway_id=pathway_id, user_address=user_address)
        )
        entry = result.first()

        if entry:
            # If the entry exists, update the num_of_calls_pending field
            session().execute(
                PathwayUsage.table().update()
                .where(PathwayUsage.table().c.pathway_id == pathway_id)
                .where(PathwayUsage.table().c.user_address == user_address)
                .values(num_of_calls_pending=entry.num_of_calls_pending + 1)
            )
        else:
            # If the entry does not exist, insert a new record
            session().execute(
                PathwayUsage.table().insert(),
                {"pathway_id": pathway_id, "user_address": user_address, "num_of_calls_pending": 1,
                 "num_of_calls_settled": 0, "created_at": date.today()}
            )

    @staticmethod
    def clear_calls_pending(pathway_id: int, user_address: str):
        """
        Moves all num_of_calls_pending to num_of_calls_settled and resets num_of_calls_pending to 0.
        """
        # Retrieve the entry from ClickHouse
        result = session().execute(
            PathwayUsage.table().select().filter_by(pathway_id=pathway_id, user_address=user_address)
        )
        entry = result.first()

        if entry and entry.num_of_calls_pending > 0:
            # Perform the update to move calls to settled
            session().execute(
                PathwayUsage.table().update()
                .where(PathwayUsage.table().c.pathway_id == pathway_id)
                .where(PathwayUsage.table().c.user_address == user_address)
                .values(
                    num_of_calls_settled=entry.num_of_calls_settled + entry.num_of_calls_pending,
                    num_of_calls_pending=0
                )
            )