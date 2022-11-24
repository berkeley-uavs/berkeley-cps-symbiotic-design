from typing import Callable

import z3

from sym_cps.contract.tool.solver.solver_interface import SolverInterface


class Z3Interface(SolverInterface):
    def __init__(self):
        super().__init__()
        self._solver = z3.Solver()
        z3.set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)
        self._model = None

    def get_fresh_variable(self, var_name: str, sort: str, **kwargs):
        if sort == "real":
            return z3.Real(var_name)
        elif sort == "integer":
            return z3.Int(var_name)
        elif sort == "boolean":
            return z3.Bool(var_name)
        elif sort == "bit_vector":
            if "bv_size" in kwargs:
                bv_size = kwargs["bv_size"]
            else:
                print("Error, no bit vector size provided")
            return z3.BitVec(var_name, bv_size)
        else:
            print("Error, Not supported type")
            

    def get_constant_value(self, sort: str, value, **kwargs):
        if sort == "real":
            return z3.RealVal(value)
        elif sort == "integer":
            return z3.IntVal(value)
        elif sort == "boolean":
            return z3.Bool(value)
        elif sort == "bit_vector":
            if "bv_size" in kwargs:
                bv_size = kwargs["bv_size"]
            else:
                print("Error, no bit vector size provided")
            return z3.BitVec(value, bv_size)
        else:
            print("Error, Not supported type")

    def generate_clause_from_function(self, sym_clause_fn: Callable, vs: dict):
        return sym_clause_fn(vs)

    def generate_clause_from_AST(self, ast):
        return NotImplementedError

    def clause_implication(self, anticedent, consequent):
        """Note: this is used for setting component selection, but may be used to do in ast"""
        return z3.Implies(anticedent, consequent)

    def clause_and(self, *args):
        return z3.And(*args)

    def clause_or(self, *args):
        return z3.Or(*args)

    def clause_equal(self, arg1, arg2):
        return arg1 == arg2

    def clause_not(self, arg):
        return z3.Not(arg)

    def clause_ge(self, arg1, arg2):
        return arg1 >= arg2

    def add_conjunction_clause(self, *args):
        self._solver.add(*args)

    def check(self) -> bool:
        ret = self._solver.check()
        #print(self._solver.assertions())
        if ret == z3.sat:
            self._model = self._solver.model()
            return True
        else:
            self._model = None
            return False

    def set_timeout(self, timeout_millisecond=100000):
        self._solver.set("timeout", timeout_millisecond)

    def get_model_for_var(self, var):
        if self._var_is_variable(var):
            ref = self._model[var]
        else:
            ref = var

        if z3.is_algebraic_value(ref):
            ref = ref.approx()
            return ref.numerator_as_long() / ref.denominator_as_long()
        elif z3.is_rational_value(ref):
            return ref.numerator_as_long() / ref.denominator_as_long()
        elif z3.is_bool(ref):
            return z3.is_true(ref)
        else:
            print("unsupported type")
        # TODO: access value for other sort

    def _var_is_variable(self, var):
        # from https://stackoverflow.com/questions/12253088/how-to-check-if-a-const-in-z3-is-a-variable-or-a-value
        return z3.is_const(var) and var.decl().kind() == z3.Z3_OP_UNINTERPRETED


if __name__ == "__main__":
    print("test")
