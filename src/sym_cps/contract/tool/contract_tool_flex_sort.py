from typing import Callable

import z3
from solver.solver_interface import SolverInterface


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
        val = solver_interface.get_constant_value(value=value)
        return val

class ContractInstance(object):
    """Class for a Contract Instance"""
    def __init__(
        self,
        name: str,
        port_list: list[ComponentInterface],
        property_list: list[ComponentInterface],
        var_dict: dict,
        guarantee: list,
        assumption: list,
        template,
        index,
        component_properties = None
    ):
        """The instance contract"""
        self._port_list: list[ComponentInterface] = port_list
        self._property_list: list[ComponentInterface] = property_list
        self._var_dict: dict = var_dict
        self._guarantee: list = guarantee
        self._assumption: list = assumption
        #self._post_constraint = post_contraint
        self._instance_name: str = name
        self._template = template
        self._index: int = index
        self._component_properties = component_properties

    @property
    def guarantee(self) -> list:
        return self._guarantee

    @property
    def assumption(self) -> list:
        return self._assumption

    def get_var(self, port_property_name: str):
        return self._var_dict[port_property_name]

    def get_port_var(self, port_name: str):
        return self._var_dict[port_name]

    def get_property_var(self, property_name: str):
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

    def get_assumption_clause(self, solver_interface: SolverInterface):
        A = self._instantiate_clauses_from_function(solver_interface=solver_interface, vs=self._vs, clause_fn=self._assumption)
        G = self._instantiate_clauses_from_function(solver_interface=solver_interface, vs=self._vs, clause_fn=self._guarantee)

    def _instantiate_clauses_from_function(self, solver_interface: SolverInterface, vs, clause_fn: Callable):
        clauses = solver_interface.generate_clause_from_function(sym_clause_fn=clause_fn, vs=vs)
        return clauses

    def _build_var_name(self, interface_name: str):
        return f"{self.template_name}_{self._index}_{self._instance_name}_{interface_name}"

    def _build_vars(self, solver_interface: SolverInterface, instance_name: str, component_properties: dict):
        v_ports = {
                    port.name: port.produce_fresh_variable(solver_interface=solver_interface ,
                                                            var_name=self._build_var_name(instance_name, port.name)) 
                                                            for port in self._port_list}
        if component_properties is not None:
            v_properties = {prop.name: 
                                prop.produce_fresh_variable(solver_interface=solver_interface, 
                                                            var_name=self._build_var_name(instance_name, prop.name)) 
                            for prop in self._property_list}
        else:
            v_properties = {prop.name: 
                                prop.produce_constant(solver_interface=solver_interface, 
                                                      value=component_properties[prop.name]) 
                            for prop in self._property_list}
        vs = {}
        vs.update(v_ports)
        vs.update(v_properties)
        return vs

class ContractTemplate(object):
    """Class for a Contract Template, Now using function as assumption/guarantee but should also be done with parser/ast"""
    def __init__(
        self, 
        name: str, 
        port_list: list[ComponentInterface], 
        property_list: list[ComponentInterface], 
        guarantee: Callable, 
        assumption: Callable,
        solver: SolverInterface
    ):
        self._port_list: list[ComponentInterface] = port_list
        self._property_list: list[ComponentInterface] = property_list
        self._guarantee: Callable = guarantee
        self._assumption: Callable = assumption
        self._count: int = 0
        self._instance_list: list[ContractInstance] = []
        self._name: str = name
        self._solver = solver

    def instantiate(self, solver_interface: SolverInterface, instance_name="", component_properties: dict = None, **kwargs) -> ContractInstance:
        """Instantiate a contract, if a component is set, then the instance is not selectable and all properties are coded
           Component is defined as a dictionary which map the property to an actual value
        """
        # check if an actual component has been assigned to this contract
        selectable = False
        if component_properties is None:
            selectable = True
        # build variable and store in vs
        vs = self._build_vars(solver_interface=solver_interface,
                              instance_name=instance_name,
                              component_properties=component_properties)
        # instantiate 
        instance = ContractInstance(
            name=instance_name,
            port_list=self._port_list,
            property_list=self._property_list,
            var_dict=vs,
            guarantee=G,
            assumption=A,
            index=self._count,
            template=self,
            component_properties=component_properties
        )
        self._add_instance(instance=instance)
        return instance

    @property
    def name(self) -> str:
        return self._name

    def _build_var_name(self, instance_name: str, interface_name: str):
        return f"{self._name}_{self._count}_{instance_name}_{interface_name}"

    def _build_vars(self, solver_interface: SolverInterface, instance_name: str, component_properties: dict):
        v_ports = {
                    port.name: port.produce_fresh_variable(solver_interface=solver_interface ,
                                                            var_name=self._build_var_name(instance_name, port.name)) 
                                                            for port in self._port_list}
        if component_properties is not None:
            v_properties = {prop.name: 
                                prop.produce_fresh_variable(solver_interface=solver_interface, 
                                                            var_name=self._build_var_name(instance_name, prop.name)) 
                            for prop in self._property_list}
        else:
            v_properties = {prop.name: 
                                prop.produce_constant(solver_interface=solver_interface, 
                                                      value=component_properties[prop.name]) 
                            for prop in self._property_list}
        vs = {}
        vs.update(v_ports)
        vs.update(v_properties)
        return vs

    def _add_instance(self, instance: ContractInstance):
        self._count += 1
        self._instance_list.append(instance)

    def _instantiate_clauses_from_function(self, solver_interface: SolverInterface, vs, clause_fn: Callable):
        clauses = solver_interface.generate_clause_from_function(sym_clause_fn=clause_fn, vs=vs)
        return clauses




class ContractSystem(object):
    def __init__(self, verbose=True):
        self._c_instance: dict[str, ContractInstance] = {}  # instance name ->  #instance
        #self._clauses: list = []
        self._constraint_clauses: list = []
        self._guarantee_clauses: list = []
        self._selection_candidate: dict[ContractInstance, dict] = {}  # map each instance to all available choice
        # the tuple contains {z3 var: actual component}
        #self._model = None
        self._solver: SolverInterface = None
        self._objective_expr = None
        self._objective_val = None
        self._objective_fn = None
        self._print_verbose = verbose

    def not_connected_ports(self) -> list[ComponentInterface]:
        """Return the list of ports that are not connected
            Useful for create system ports 
        """
        return NotImplementedError

    def is_concrete(self):
        """Check whether the whole system is concrete, meaning that all component has been selected"""
        for inst in self._c_instance.values():
            if inst.is_selectable:
                return False 
        return True

    def print_debug(self, *args):
        if self._print_verbose:
            print(*args)

    def check_refinement(self, sys_inst: ContractInstance):
        self.print_debug("Add instance: ", sys_inst.instance_name)
        self._c_instance[sys_inst.instance_name] = sys_inst
        self._selection_candidate[sys_inst] = {}
        # self._guarantee_clauses.extend(sys_inst.assumption)
        # self._constraint_clauses.extend(sys_inst.guarantee)
        #self._clauses.extend(sys_inst.assumption)
        #self._clauses.append(z3.Not(z3.And(*sys_inst.guarantee)))

    def add_instance(self, inst1: ContractInstance):
        self.print_debug("Add instance: ", inst1.instance_name)
        self._c_instance[inst1.instance_name] = inst1
        self._selection_candidate[inst1] = {}
        # self._constraint_clauses.extend(inst1.assumption)
        # self._guarantee_clauses.extend(inst1.guarantee)

    def compose(self, inst1: ContractInstance, inst2: ContractInstance, connection_map: list[tuple[str, str]]):
        """Connect port of inst1 to inst2
        port map is a list that indicate the connection from inst1 to inst2
        """
        for port1, port2 in connection_map:
            self._guarantee_clauses.append(inst1.get_port_var(port1) == inst2.get_port_var(port2))

    def set_selection(self, inst: ContractInstance, candidate_list: list):
        if not inst.is_selectable:
            print(f"Error, instance {inst.instance_name} has been instantiated with a concrete component and thus cannot be selected.")
        if inst.instance_name not in self._c_instance:
            print(f"Error, instance {inst.instance_name} has not been added. Use add_instance")
            return False

        selection_dict = {}
        # set property
        for candidate in candidate_list:
            use_v = z3.Bool(f"{inst.instance_name}_use_{candidate.id}")
            property_dict = self._property_interface_fn(candidate)
            assignment_constraint = [
                inst.get_property_var(prop_name) == property_dict[prop_name] for prop_name in inst.property_name_list
            ]
            self._guarantee_clauses.append(z3.Implies(use_v, z3.And(*assignment_constraint)))
            selection_dict[use_v] = candidate

        self._selection_candidate[inst] = selection_dict

        # constraint that no multiple chosen
        for v, cand in selection_dict.items():
            not_v2s = [z3.Not(v2) for v2 in selection_dict.keys() if v.get_id() != v2.get_id()]
            self._guarantee_clauses.append(z3.Implies(v, z3.And(*not_v2s)))

        # select one
        self._guarantee_clauses.append(z3.Or(*(selection_dict.keys())))

    def set_env(self, clause):
        self._guarantee_clauses.append(clause)

    def set_objective(self, expr, value, evaluate_fn):
        self._objective_expr = expr
        self._objective_val = value
        self._objective_fn = evaluate_fn

    def calculate_objective(self):
        return self._objective_fn()

    def get_var(self, inst_name, port_property_name):
        return self._c_instance[inst_name].get_var(port_property_name=port_property_name)


    def solve_contract(self):
        self._solver = z3.Solver()
        self._solver.add(z3.Not(z3.And(*self._constraint_clauses)))
        self._solver.add(self._guarantee_clauses)
        self._solver.add(self._objective_expr >= self._objective_val)
        z3.set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)
        # print(self._solver.assertions)
        ret = self._solver.check()
        # print(self._solver.assertions())
        if ret == z3.sat:  # SAT
            self.print_debug("SAT")
            self._model = self._solver.model()
            # print(model)
            self.print_metric()
            # selection_result = self.get_component_selection()
            # self.print_selection_result(selection_result)
            
            return True
        else:
            self.print_debug("UNSAT")
            return False

    def solve(self):
        self._solver = z3.Solver()
        self._solver.add(self._constraint_clauses)
        self._solver.add(self._guarantee_clauses)
        self._solver.add(self._objective_expr >= self._objective_val)
        z3.set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)
        # print(self._solver.assertions)
        ret = self._solver.check()
        # print(self._solver.assertions())
        if ret == z3.sat:  # SAT
            self.print_debug("SAT")
            self._model = self._solver.model()
            # print(model)
            selection_result = self.get_component_selection()
            self.print_selection_result(selection_result)
            self.print_metric()
            return True
        else:
            self.print_debug("UNSAT")
            return False

    def solve_optimize(self, max_iter=0, timeout_millisecond=100000):
        num_iter = 0
        selection_result = None
        self._solver = z3.Solver()
        # self._solver = z3.Optimize()
        self._solver.add(self._constraint_clauses)
        self._solver.add(self._guarantee_clauses)
        # self._solver.push()
        self._solver.add(self._objective_expr >= self._objective_val)
        self._solver.set("timeout", timeout_millisecond)
        ret = self._solver.check()
        while ret == z3.sat:
            self._model = self._solver.model()
            selection_result = self.get_component_selection()
            self.print_debug(f"Iteration: {num_iter}")
            self.print_selection_result(selection_result)
            self.print_metric()
            # count progress
            if num_iter >= max_iter:
                break
            else:
                num_iter += 1
            # set for next iteration
            new_value = self.calculate_objective()
            # self._solver.pop()
            self._solver.add(self._objective_expr >= new_value)
            ret = self._solver.check()
        if selection_result is None:
            self.print_debug("Fail.....")

        return selection_result

    def get_metric(self, inst_name, port_property_name):
        var = self.get_var(inst_name=inst_name, port_property_name=port_property_name)
        ref = self._model[var]
        if z3.is_algebraic_value(ref):
            ref = ref.approx()
        return ref.numerator_as_long() / ref.denominator_as_long()

    def get_metric_inst(self, inst: ContractInstance, port_property_name: str):
        var = inst.get_var(port_property_name=port_property_name)
        ref = self._model[var]
        if z3.is_algebraic_value(ref):
            ref = ref.approx()
        return ref.numerator_as_long() / ref.denominator_as_long()

    def get_component_selection(self) -> dict:  # ContractInstance to Candidate Component
        ret = {}
        for inst, selection_dict in self._selection_candidate.items():
            for v, cand in selection_dict.items():
                if z3.is_true(self._model[v]):
                    ret[inst] = cand
                    break
        return ret

    def print_metric(self):
        if not self._print_verbose:
            return
        print(f"===================Component Selection Metric=====================")
        for inst in self._c_instance.values():
            print(f" ")
            print(f"    Instance: {inst.instance_name}")
            for port_name in inst.port_name_list:
                val = self.get_metric(inst_name=inst.instance_name, port_property_name=port_name)
                print(f"        {port_name}: {val}")
            for property_name in inst.property_name_list:
                val = self.get_metric(inst_name=inst.instance_name, port_property_name=property_name)
                print(f"        {property_name}: {val}")
        print("==================================================================")

    def print_selection_result(self, ret):
        if not self._print_verbose:
            return
        print(f"===================Component Selection Result=====================")
        for inst, cand in ret.items():
            property_dict = self._property_interface_fn(cand)
            cand_name = property_dict["name"]
            print(f"    {inst.instance_name}: {cand_name}")
        print("==================================================================")

    def check_candidate_valid(self):
        for inst in self._c_instance.values():
            if inst not in self._selection_candidate:
                if inst.property_name_list:
                    print(f"Error: Instance {inst.instance_name} requires properties but has no selection available!")
                    return False
        return True
