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

def get_metrics_action_engine(db_connection_string: str = ...) -> Engine: ...

class MetricActionType(Enum):
    GAS = 'GAS'
    FEES = 'FEES'
    WRAP = 'WRAP'
    UNWRAP = 'UNWRAP'
    APPROVE = 'APPROVE'
    SWAP = 'SWAP'
    OPEN_POSITION = 'OPEN_POSITION'
    CLOSE_POSITION = 'CLOSE_POSITION'

class MetricsActionTable(SQLModel, table=True):
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

class MetricsActionHandler:
    engine: Incomplete
    def __init__(self, db_connection_string) -> None: ...
    def create_tables(self) -> None: ...
    def add_metric(self, metric: str) -> None: ...
    def get_metrics_action(self, strategy_id: str | None = None, metric_type: MetricActionType | None = None, wallet_address: str | None = None): ...
    def metric_exists(self, metric_type: str, action_id: str) -> bool: ...
