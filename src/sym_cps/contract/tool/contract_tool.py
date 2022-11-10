from typing import Callable, Any
import z3

class ContractInstance(object):
    def __init__(self, name: str, port_name_list: list, property_name_list: list, z3_var_dict: dict, guarantee: list, assumption: list, template, index):
        """The instance contract"""
        self._port_name_list = port_name_list
        self._property_name_list = property_name_list
        self._z3_var_dict = z3_var_dict
        self._guarantee = guarantee
        self._assumption = assumption
        self._instance_name = name
        self._template = template
        self._index = index

    @property
    def guarantee(self) -> list:
        return self._guarantee

    @property
    def assumption(self) -> list:
        return self._assumption

    def get_var(self, port_property_name: str):
        return self._z3_var_dict[port_property_name]

    def get_port_var(self, port_name: str):
        return self._z3_var_dict[port_name]

    def get_property_var(self, property_name: str):
        return self._z3_var_dict[property_name]

    @property
    def instance_name(self) -> str:
        return self._instance_name

    @property
    def template_name(self) -> str:
        return self._template.name

    @property
    def property_name_list(self) -> list:
        return self._property_name_list
    @property
    def port_name_list(self) -> list:
        return self._port_name_list

    @property
    def template_name(self) -> str:
        return self._template.name

    @property
    def index(self) -> int:
        return self._index

class ContractTemplate(object):
    def __init__(self, name: str, port_name_list: list, property_name_list: list, guarantee: Callable, assumption: Callable):
        self._port_name_list = port_name_list
        self._property_name_list = property_name_list
        self._guarantee = guarantee
        self._assumption = assumption
        self._count = 0
        self._instance_list: list[ContractInstance] = []
        self._name = name



    def instantiate(self, instance_name = "", **kwargs) -> ContractInstance:
        """Instantiate a contract"""
        vs = {v: z3.Real(f"{self._name}_{self._count}_{instance_name}_{v}") for v in self._port_name_list}
        vs.update({v: z3.Real(f"{self._name}_{self._count}_{instance_name}_{v}") for v in self._property_name_list})
        A = self._assumption(vs, **kwargs)
        G = self._guarantee(vs, **kwargs)
        instance = ContractInstance(name=instance_name,
                                    port_name_list=self._port_name_list, 
                                    property_name_list=self._property_name_list,
                                    z3_var_dict=vs, 
                                    guarantee=G,
                                    assumption=A,
                                    index=self._count,
                                    template=self)
        self._instance_list.append(instance)
        self._count += 1
        return instance
    
    @property
    def name(self) -> str:
        return self._name

class ContractManager(object):
    def __init__(self, property_interface_fn: Callable):
        self._c_instance: dict[str, ContractInstance] = {}# instance name ->  #instance
        self._clauses: list = []
        self._selection_candidate: dict[ContractInstance, dict] = {} # map each instance to all available choice
            # the tuple contains {z3 var: actual component}
        self._property_interface_fn = property_interface_fn
        self._model = None
        self._solver = None
        self._objective_expr = None
        self._objective_val = None
        self._objective_fn = None
        self._print_verbose = True

    def print_debug(self, *args):
        if self._print_verbose:
            print(*args)

    def add_instance(self, inst1: ContractInstance):
        self.print_debug("Add instance: ", inst1.instance_name)
        self._c_instance[inst1.instance_name] = inst1
        self._selection_candidate[inst1] = {}
        self._clauses.extend(inst1.guarantee)
        self._clauses.extend(inst1.assumption)

    def compose(self, inst1: ContractInstance, inst2:ContractInstance, connection_map: list[tuple[str, str]]):
        """Connect port of inst1 to inst2
        port map is a list that indicate the connection from inst1 to inst2
        """
        for port1, port2 in connection_map:
            self._clauses.append(inst1.get_port_var(port1) == inst2.get_port_var(port2))

    def set_selection(self, inst: ContractInstance, candidate_list: list):
        if inst.instance_name not in self._c_instance:
            print(f"Error, instance {inst.instance_name} has not been added. Use add_instance")
            return False

        selection_dict = {}
        # set property
        for candidate in candidate_list:
            use_v = z3.Bool(f"{inst.instance_name}_use_{candidate.id}")
            property_dict = self._property_interface_fn(candidate)
            assignment_constraint = [inst.get_property_var(prop_name) == property_dict[prop_name] for prop_name in inst.property_name_list]
            self._clauses.append(z3.Implies( use_v, 
                                             z3.And(*assignment_constraint)
            ))
            selection_dict[use_v] = candidate

        self._selection_candidate[inst] = selection_dict

        # constraint that no multiple chosen
        for v, cand in selection_dict.items():
            not_v2s = [z3.Not(v2) for v2 in selection_dict.keys() if v.get_id() != v2.get_id()]
            self._clauses.append(z3.Implies(v, z3.And(*not_v2s)))   

        # select one
        self._clauses.append(z3.Or(*(selection_dict.keys())))

    def set_env(self, clause):
        self._clauses.append(clause)

    def set_objective(self, expr, value, evaluate_fn):
        self._objective_expr = expr
        self._objective_val = value
        self._objective_fn = evaluate_fn

    def calculate_objective(self):
        return self._objective_fn()

    def get_var(self, inst_name, port_property_name):
        return self._c_instance[inst_name].get_var(port_property_name=port_property_name)

    def solve(self):
        self._solver = z3.Solver()
        self._solver.add(self._clauses)
        self._solver.add(self._objective_expr >= self._objective_val)
        z3.set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)
        #print(self._solver.assertions)
        ret = self._solver.check()
        #print(self._solver.assertions())
        if ret == z3.sat:# SAT
            print("SAT")
            self._model = self._solver.model()      
            #print(model)
            selection_result = self.get_component_selection()
            self.print_selection_result(selection_result)
            self.print_metric()
            return True
        else:
            print("UNSAT")
            return False

    def solve_optimize(self,  max_iter = 0, timeout_millisecond = 100000):
        num_iter = 0
        selection_result = None
        self._solver = z3.Solver()
        #self._solver = z3.Optimize()
        self._solver.add(self._clauses)
        #self._solver.push()
        self._solver.add(self._objective_expr >= self._objective_val)
        self._solver.set("timeout", timeout_millisecond)
        ret = self._solver.check()
        while ret == z3.sat:
            self._model = self._solver.model()   
            selection_result = self.get_component_selection()
            print(f"Iteration: {num_iter}")
            self.print_selection_result(selection_result)
            self.print_metric()
            # count progress
            if num_iter >= max_iter:
                break
            else: 
                num_iter += 1
            # set for next iteration
            new_value = self.calculate_objective()
            #self._solver.pop()
            self._solver.add(self._objective_expr >= new_value)
            ret = self._solver.check()
        if selection_result is None:
            print("Fail.....")

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

    def get_component_selection(self) -> dict: # ContractInstance to Candidate Component
        ret = {}
        for inst, selection_dict in self._selection_candidate.items():
            for v, cand in selection_dict.items():
                if z3.is_true(self._model[v]):
                    ret[inst] = cand
                    break
        return ret

    def print_metric(self):
        print(f"===================Component Selection Metric=====================")
        for inst in self._c_instance.values():
            print(f" ")
            print(f"    Instance: {inst.instance_name}")
            for port_name in inst.port_name_list:
                val = self.get_metric(inst_name = inst.instance_name, port_property_name=port_name)
                print(f"        {port_name}: {val}")
            for property_name in inst.property_name_list:
                val = self.get_metric(inst_name = inst.instance_name, port_property_name=property_name)
                print(f"        {property_name}: {val}")
        print("==================================================================")

    def print_selection_result(self, ret):
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

            

