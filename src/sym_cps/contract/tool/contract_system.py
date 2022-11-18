from sym_cps.contract.tool.contract_instance import ContractInstance
from sym_cps.contract.tool.component_interface import ComponentInterface
from sym_cps.contract.tool.solver.solver_interface import SolverInterface

class ContractSystem(object):
    """Define the system in horizontal view, in this view, contracts are interacting using their interface"""
    def __init__(self, verbose=True):
        self._c_instance: dict[str, ContractInstance] = {}  # instance name ->  #instance
        #self._clauses: list = []
        self._constraint_clauses: list = []# list to make compositon
        self._guarantee_clauses: list = []# list to make compositon
        self._system_clauses: list = []# list to contain all the connection and selection constraint encoding
        self._selection_candidate: dict[ContractInstance, dict] = {}  # map each instance to all available choice
        # the tuple contains {z3 var: actual component}
        #self._model = None
        self._solver: SolverInterface = None
        self._objective_expr = None
        self._objective_val = None
        self._objective_fn = None
        self._print_verbose = verbose

    def set_solver(self, solver_interface: SolverInterface):
        self._solver = solver_interface

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

    def check_refinement(self, sys_inst: ContractInstance, sys_connection_map: dict[str, list[tuple[str, str]]]):
        """sys_connection_map: key: instance name, then list of connection from sys_inst to it
        Example: {"propeller_a": [("thrust_from_propeller_a", "thrust_a")]}
        Should accept ComponentInterface directly.
        """
        self.print_debug("Check Refinement Invoked!")
        self._clear_clauses()
        sys_inst.build_clauses(solver_interface=self._solver)
        self._build_refinement_system(sys_inst=sys_inst)
        self._build_connection_one_to_multi(sys_inst, sys_connection_map=sys_connection_map)
        self._solver.add_conjunction_clause(self._guarantee_clauses)
        self._solver.add_conjunction_clause(self._system_clauses)
        self._solver.add_conjunction_clause(
            self._solver.clause_not(
                self._solver.clause_and(*self._constraint_clauses)
            )
        )
        is_sat = self._solver.check()    
        if is_sat and self._print_verbose:
            self.print_metric()
        return is_sat

    def find_behavior(self, sys_inst: ContractInstance, sys_connection_map: dict[str, list[tuple[str, str]]]):
        self.print_debug("Find Behavior Invoked!")
        self._clear_clauses()
        sys_inst.build_clauses(solver_interface=self._solver)
        self._build_find_behavior_system(sys_inst=sys_inst)
        self._build_connection_one_to_multi(sys_inst, sys_connection_map=sys_connection_map)
        self._solver.add_conjunction_clause(self._guarantee_clauses)
        self._solver.add_conjunction_clause(self._system_clauses)
        self._solver.add_conjunction_clause(self._constraint_clauses)
        is_sat = self._solver.check()    
        if is_sat and self._print_verbose:
            self.print_debug("SAT")
            self.print_metric()
            self.print_instance_metric(sys_inst)
        else:
            self.print_debug("UNSAT")
        return is_sat

    def select(self, sys_inst: ContractInstance, 
                     sys_connection_map: dict[str, list[tuple[str, str]]],
                     max_iter: int,
                     timeout_milliseconds: int):
        self.print_debug("Select Component!")
        self._clear_clauses()
        sys_inst.build_clauses(solver_interface=self._solver)
        self._build_find_behavior_system(sys_inst=sys_inst)
        self._build_connection_one_to_multi(sys_inst, sys_connection_map=sys_connection_map)
        self._solver.add_conjunction_clause(self._guarantee_clauses)
        self._solver.add_conjunction_clause(self._constraint_clauses)
        self._solver.add_conjunction_clause(self._system_clauses)
        self._solver.set_timeout(timeout_millisecond=timeout_milliseconds)
        is_sat = self._solver.check()
        num_iter = 0
        selection_result = None
        while is_sat:
            selection_result = self.get_component_selection()
            if self._print_verbose:
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
            self._solver.add_conjunction_clause(self._solver.clause_ge(self._objective_expr, new_value))
            ret = self._solver.check()

        if selection_result is None:
            self.print_debug("Fail.....")

        return selection_result

    def _clear_clauses(self):
        self._constraint_clauses = []
        self._guarantee_clauses = []

    def _build_refinement_system(self, sys_inst: ContractInstance):
        for inst in self._c_instance.values():
            self._constraint_clauses.extend(inst.assumption_clauses)
            self._guarantee_clauses.extend(inst.guarantee_clauses)
        self._constraint_clauses.extend(sys_inst.guarantee_clauses)
        self._guarantee_clauses.extend(sys_inst.assumption_clauses)
    

    def _build_connection_one_to_multi(self, sys_inst:ContractInstance, sys_connection_map: dict[str, list[tuple[str, str]]]):
        for inst_name, connection_map in sys_connection_map.items():
            inst = self._c_instance[inst_name]
            self.compose(inst1=sys_inst, inst2=inst, connection_map=connection_map)

    def _build_find_behavior_system(self, sys_inst: ContractInstance):
        for inst in self._c_instance.values():
            self._constraint_clauses.extend(inst.assumption_clauses)
            self._guarantee_clauses.extend(inst.guarantee_clauses)
        self._constraint_clauses.extend(sys_inst.assumption_clauses)
        self._guarantee_clauses.extend(sys_inst.guarantee_clauses)        

    def add_instance(self, inst1: ContractInstance):
        self.print_debug("Add instance: ", inst1.instance_name)
        inst1.build_clauses(solver_interface=self._solver)
        if inst1.instance_name in self._c_instance:
            raise Exception(f"Duplicated contract name {inst1.instance_name} in the system")
        self._c_instance[inst1.instance_name] = inst1
        self._selection_candidate[inst1] = {}
        # self._constraint_clauses.extend(inst1.assumption)
        # self._guarantee_clauses.extend(inst1.guarantee)

    def compose(self, inst1: ContractInstance, inst2: ContractInstance, connection_map: list[tuple[str, str]]):
        """Connect port of inst1 to inst2
        port map is a list that indicate the connection from inst1 to inst2
        """
        for port1, port2 in connection_map:
            self._system_clauses.append(self._solver.clause_equal(inst1.get_port_var(port1), inst2.get_port_var(port2)))

    def set_selection(self, inst: ContractInstance, candidate_list: list[dict]):
        """Set selection for a instance
        candidte_list: a list where each element represents a component, the element should be 
        a dictionary which map the name of the property to an actual value
        """
        if not inst.is_selectable:
            print(f"Error, instance {inst.instance_name} has been instantiated with a concrete component and thus cannot be selected.")
        if inst.instance_name not in self._c_instance:
            print(f"Error, instance {inst.instance_name} has not been added. Use add_instance")
            return False

        selection_dict = {}
        # set property
        for candidate in candidate_list:
            use_v = self._solver.get_fresh_variable(var_name=f"{inst.instance_name}_use_{candidate.id}", sort="bool")
            assignment_constraint = [
                self._solver.clause_equal(inst.get_property_var(prop_name), candidate[prop_name]) for prop_name in inst.property_name_list
            ]
            self._system_clauses.append(
                self._solver.clause_implication(use_v, self._solver.clause_and(*assignment_constraint))
            )
            selection_dict[use_v] = candidate

        self._selection_candidate[inst] = selection_dict

        # constraint that no multiple chosen
        for v, cand in selection_dict.items():
            not_v2s = [self._solver.clause_not(v2) for v2 in selection_dict.keys() if v.get_id() != v2.get_id()]
            self._system_clauses.append(
                self._solver.clause_implication(v, self._solver.clause_and(*not_v2s))
            )

        # select one
        self._guarantee_clauses.append(
            self._solver.clause_or(*(selection_dict.keys()))
        )

    def set_objective(self, expr, value, evaluate_fn):
        self._objective_expr = expr
        self._objective_val = value
        self._objective_fn = evaluate_fn
        self._solver.add_conjunction_clause(self._solver.clause_ge(self._objective_expr, self._objective_val))

    def calculate_objective(self):
        return self._objective_fn()

    def get_var(self, inst_name, port_property_name):
        return self._c_instance[inst_name].get_var(port_property_name=port_property_name)

    def get_metric(self, inst_name, port_property_name):
        var = self.get_var(inst_name=inst_name, port_property_name=port_property_name)
        return self._solver.get_model_for_var(var=var)

    def get_metric_inst(self, inst: ContractInstance, port_property_name: str):
        var = inst.get_var(port_property_name=port_property_name)
        return self._solver.get_model_for_var(var=var)

    def get_component_selection(self) -> dict:  # ContractInstance to Candidate Component
        ret = {}
        for inst, selection_dict in self._selection_candidate.items():
            for v, cand in selection_dict.items():
                is_selected = self._solver.get_model_for_var(var=v)
                if is_selected:
                    ret[inst] = cand
                    break
        return ret

    def print_metric(self):
        if not self._print_verbose:
            return
        print(f"===================Component Selection Metric=====================")
        for inst in self._c_instance.values():
            self.print_instance_metric(inst=inst)
        print("==================================================================")

    def print_instance_metric(self, inst: ContractInstance):
        print(f" ")
        print(f"    Instance: {inst.instance_name}")
        for port in inst.port_list:
            val = self.get_metric_inst(inst=inst, port_property_name=port.name)
            print(f"        {port.name}: {val}")
        for prop in inst.property_list:
            val = self.get_metric_inst(inst=inst, port_property_name=prop.name)
            print(f"        {prop.name}: {val}")

    def print_selection_result(self, ret):
        if not self._print_verbose:
            return
        print(f"===================Component Selection Result=====================")
        for inst, cand in ret.items():
            cand_name = cand["name"]
            print(f"    {inst.instance_name}: {cand_name}")
        print("==================================================================")

    def check_candidate_valid(self):
        for inst in self._c_instance.values():
            if inst not in self._selection_candidate:
                if inst.is_selectable:
                    print(f"Error: Instance {inst.instance_name} requires properties but has no selection available!")
                    return False
        return True