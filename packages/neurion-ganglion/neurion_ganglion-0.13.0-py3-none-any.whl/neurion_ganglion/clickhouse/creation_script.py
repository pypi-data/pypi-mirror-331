import dotenv

from neurion_ganglion.clickhouse.ion_usage import IonUsage
from neurion_ganglion.clickhouse.pathway_usage import PathwayUsage

dotenv.load_dotenv()
from neurion_ganglion.clickhouse import engine


def init_db():
    IonUsage.table().create(engine())
    PathwayUsage.table().create(engine())

init_db()