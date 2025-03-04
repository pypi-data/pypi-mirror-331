from _typeshed import Incomplete
from src.almanak_library.enums import Chain as Chain, Network as Network
from src.strategy.strategies import StrategyDynamicLP as StrategyDynamicLP, StrategyTroubleshootClosePositions as StrategyTroubleshootClosePositions, StrategyTutorialHelloWorld as StrategyTutorialHelloWorld
from src.strategy.strategy_base import Strategy as Strategy
from src.utils.utils import get_web3_by_network_and_chain as get_web3_by_network_and_chain

class StrategyFactory:
    strategies: Incomplete
    @staticmethod
    def create_strategy(strategy_name, parameters): ...
    @staticmethod
    def get_strategies(): ...

IS_AGENT_DEPLOYMENT: Incomplete
active_strategy_name: Incomplete
import_aliases: Incomplete
abs_path: Incomplete

def get_strategy_from_module(): ...

class StrategyFactoryOverride(StrategyFactory):
    strategies: Incomplete
StrategyFactory = StrategyFactoryOverride

def get_parameters_from_config(config: dict, strategy_id: str, verbose: bool = True) -> dict: ...
def create_strategy_from_config(config: dict, strategy_id: str) -> Strategy:
    """
    Extracts shared and specific strategy configuration, merges shared parameters with specific parameters
    for the strategy corresponding to the strategy_id received, and create the strategy instance using the StrategyFactory.

    Returns:
       Strategy instance (or None if the strategy_id is not found).
    """
def get_strategy_ids_from_config(config: dict) -> list[str]: ...
