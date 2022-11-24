from typing import Callable

from sym_cps.contract.tool.component_interface import ComponentInterface
from sym_cps.contract.tool.contract_template import ContractTemplate
from sym_cps.contract.tool.solver.solver_interface import SolverInterface


class ContractInstance(object):
    """Class for a Contract Instance
    The component_properties set an antual property value to the contract, making the contract non-selectable
    """

    def __init__(
        self,
        template: ContractTemplate,
        instance_name: str,
        component_properties: dict = None,
        solver_interface: SolverInterface = None,
    ):

        self._port_list: list[ComponentInterface] = template.port_list
        self._property_list: list[ComponentInterface] = template.property_list
        self._guarantee: Callable = template.guarantee
        self._assumption: Callable = template.assumption
        self._component_properties: dict = component_properties
        self._var_dict: dict = {}
        self._instance_name = instance_name
        self._template: ContractTemplate = template
        self._index: int = template.add_instance(self)
        self._solver_interface: SolverInterface = solver_interface

        self._assumption_clauses = None
        self._guarantee_clauses = None

    @property
    def guarantee(self) -> Callable:
        return self._guarantee

    @property
    def assumption(self) -> Callable:
        return self._assumption

    @property
    def assumption_clauses(self):
        return self._assumption_clauses

    @property
    def guarantee_clauses(self):
        return self._guarantee_clauses

    def get_var(self, port_property_name: str):
        return self._var_dict[port_property_name]

    def get_port_var(self, port_name: str):
        return self._var_dict[port_name]

    def get_property_var(self, property_name: str):
        if property_name not in self._var_dict:
            print(f"Error, name {property_name} not found")
        return self._var_dict[property_name]

    @property
    def instance_name(self) -> str:
        return self._instance_name

    @property
    def template_name(self) -> str:
        return self._template.name

    @property
    def property_list(self) -> list[ComponentInterface]:
        return self._property_list

    @property
    def port_list(self) -> list[ComponentInterface]:
        return self._port_list

    @property
    def template_name(self) -> str:
        return self._template.name

    @property
    def index(self) -> int:
        return self._index

    @property
    def is_selectable(self) -> bool:
        return self._component_properties is None

    @property
    def solver_interface(self) -> SolverInterface:
        return self._solver_interface

    def set_solver(self, solver_interface: SolverInterface):
        self._solver_interface = solver_interface

    def set_component(self, component_properties: dict):
        self._component_properties = component_properties

    def reset_clauses(self):
        self._var_dict = {}
        self._assumption_clauses = None
        self._guarantee_clauses = None

    def build_clauses(self, solver_interface: SolverInterface):
        self.set_solver(solver_interface)
        self.reset_clauses()
        self._build_port_vars(solver_interface=self.solver_interface)
        self._build_property_vars(
            solver_interface=self.solver_interface, component_properties=self._component_properties
        )
        self._assumption_clauses = self._instantiate_clauses_from_function(
            solver_interface=solver_interface, vs=self._var_dict, clause_fn=self.assumption
        )
        self._guarantee_clauses = self._instantiate_clauses_from_function(
            solver_interface=solver_interface, vs=self._var_dict, clause_fn=self.guarantee
        )

    def _instantiate_clauses_from_function(self, solver_interface: SolverInterface, vs, clause_fn: Callable):
        clauses = solver_interface.generate_clause_from_function(sym_clause_fn=clause_fn, vs=vs)
        return clauses

    def instantiate_clauses_from_function(self, solver_interface: SolverInterface, clause_fn: Callable):
        return self._instantiate_clauses_from_function(solver_interface=solver_interface, vs=self._var_dict, clause_fn=clause_fn)

    def _build_var_name(self, interface_name: str):
        return f"{self.template_name}_{self.index}_{self.instance_name}_{interface_name}"

    def _build_port_vars(self, solver_interface: SolverInterface):
        v_ports = {
            port.name: port.produce_fresh_variable(
                solver_interface=solver_interface, var_name=self._build_var_name(interface_name=port.name)
            )
            for port in self.port_list
        }
        self._var_dict.update(v_ports)

    def _build_property_vars(self, solver_interface: SolverInterface, component_properties: dict):
        v_properties = None
        if component_properties is not None:
            v_properties = {
                prop.name: prop.produce_constant(
                    solver_interface=solver_interface, value=component_properties[prop.name]
                )
                for prop in self.property_list
            }
        else:
            v_properties = {
                prop.name: prop.produce_fresh_variable(
                    solver_interface=solver_interface, var_name=self._build_var_name(interface_name=prop.name)
                )
                for prop in self.property_list
            }
        self._var_dict.update(v_properties)
