from abc import ABC, abstractmethod
from typing import Callable


class SolverInterface(ABC):
    """Temporary not used, but should be able to insert into AST to create clause"""

    def __init__(self):
        pass

    @abstractmethod
    def get_fresh_variable(self, var_name: str, sort: str, **kwargs):
        pass

    @abstractmethod
    def get_constant_value(self, sort: str, value, **kwargs):
        pass

    @abstractmethod
    def generate_clause_from_AST(self, ast):
        return NotImplementedError

    @abstractmethod
    def generate_clause_from_function(self, sym_clause_fn: Callable, vs: dict):
        """vs: the dictionary that contains map the name in the contract template to actual variables"""

    @abstractmethod
    def clause_implication(self, anticedent, consequent):
        """Note: this is used for setting component selection, but may be used to do in ast"""

    @abstractmethod
    def set_timeout(self, timeout_millisecond=100000):
        pass

    @abstractmethod
    def clause_and(self, *args):
        pass

    @abstractmethod
    def clause_or(self, *args):
        pass

    @abstractmethod
    def clause_not(self, arg):
        pass

    @abstractmethod
    def clause_equal(self, arg1, arg2):
        pass

    @abstractmethod
    def clause_ge(self, arg1, arg2):
        pass

    @abstractmethod
    def clause_gt(self, arg1, arg2):
        pass

    @abstractmethod
    def add_conjunction_clause(self, *args):
        pass

    @abstractmethod
    def check(self) -> bool:
        pass

    @abstractmethod
    def get_model_for_var(self, var):
        pass
