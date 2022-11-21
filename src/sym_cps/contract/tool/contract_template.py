from typing import Callable

from sym_cps.contract.tool.component_interface import ComponentInterface


class ContractTemplate(object):
    """Class for a Contract Template, Now using function as assumption/guarantee but should also be done with parser/ast"""

    def __init__(
        self,
        name: str,
        port_list: list[ComponentInterface],
        property_list: list[ComponentInterface],
        guarantee: Callable,
        assumption: Callable,
    ):
        self._port_list: list[ComponentInterface] = port_list
        self._property_list: list[ComponentInterface] = property_list
        self._guarantee: Callable = guarantee
        self._assumption: Callable = assumption
        self._count: int = 0
        self._instance_list: list = []
        self._name: str = name

    @property
    def guarantee(self) -> Callable:
        return self._guarantee

    @property
    def assumption(self) -> Callable:
        return self._assumption

    @property
    def property_list(self) -> list[ComponentInterface]:
        return self._property_list

    @property
    def port_list(self) -> list[ComponentInterface]:
        return self._port_list

    @property
    def name(self) -> str:
        return self._name

    def add_instance(self, instance) -> int:
        index = self._count
        self._count += 1
        self._instance_list.append(instance)
        return index
