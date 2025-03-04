from _typeshed import Incomplete
from enum import Enum
from sqlalchemy.future.engine import Engine as Engine
from sqlmodel import SQLModel
from src.utils.config import Config as Config

STORAGE_DIR: Incomplete
LOCAL_DB_PATH: Incomplete
READ_ONLY_MODE: Incomplete
IS_AGENT_DEPLOYMENT: Incomplete
METRICS_DB_CONNECTION_STRING: Incomplete

def get_metrics_agg_engine(db_connection_string: str = ...) -> Engine: ...

class MetricAggType(Enum):
    INITIALIZATION = 'INITIALIZATION'
    TEARDOWN = 'TEARDOWN'
    STRATEGY_BALANCE = 'STRATEGY_BALANCE'
    WALLET_BALANCE = 'WALLET_BALANCE'
    SNAPSHOT = 'SNAPSHOT'
    REBALANCE_TRIGGER = 'REBALANCE_TRIGGER'

class MetricsAggTable(SQLModel, table=True):
    __tablename__: str
    id: int
    time: str
    block_number: int | None
    metric_type: str
    strategy_id: str
    action_id: str
    bundle_id: str
    wallet_address: str
    details: dict
    __table_args__: Incomplete

class MetricsAggHandler:
    engine: Incomplete
    def __init__(self, db_connection_string) -> None: ...
    def create_tables(self) -> None: ...
    def add_metric(self, metric: str) -> None: ...
    def get_metrics_agg(self, strategy_id: str | None = None, metric_type: MetricAggType | str | None = None, wallet_address: str | None = None): ...
