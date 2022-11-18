from sym_cps.contract.tool.solver.solver_interface import SolverInterface

class ComponentInterface(object):
    """Class for defining interface between different component
    """
    def __init__(self, name:str, sort:str):
        self._name = name
        self._sort = sort

    @property
    def name(self):
        return self._name
    @property
    def sort(self):
        return self._sort

    def produce_fresh_variable(self, solver_interface: SolverInterface, var_name: str):
        """Produce a fresh variable in the solver
        solver_interface: the solver to use
        var_name: the name to be encode in the underlying solver
        """
        var = solver_interface.get_fresh_variable(var_name=var_name, sort=self._sort)
        return var
    
    def produce_constant(self, solver_interface: SolverInterface, value):
        val = solver_interface.get_constant_value(value=value, sort=self._sort)
        return val