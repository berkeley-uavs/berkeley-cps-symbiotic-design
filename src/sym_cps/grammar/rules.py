from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto

import numpy as np
from igraph import Edge, Graph, Vertex


class GrammarSymbols(Enum):
    UNOCCUPIED = auto()
    BOUNDARY = auto()
    ANYTHING = auto()
    FUSELAGE = auto()
    WING = auto()
    ROTOR = auto()
    BODY = auto()
    SHORT_WING = auto()
    MEDIUM_WING = auto()
    LONG_WING = auto()
    HUB = auto()
    TUBE = auto()
    CONNECTOR = auto()


class Neighbors(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    FRONT = auto()
    REAR = auto()


class Rule:
    def __init__(self, lhs: Graph, rhs: Graph):
        self.lhs = lhs  # 3 x 3 x 3 array with 1,1,1 being the center
        self.rhs = rhs  # same shape


'''
def get_applicable_matches(rule: Rule, design_topo_matrix: np.array):
    """Generates all applicable matches for rule in graph."""
    applicable_matches = []
    for i in range(design_topo_matrix.shape[0]):
        for j in range(design_topo_matrix.shape[1]):
            for k in range(design_topo_matrix.shape[2]):
                if is_applicable_match(rule, design_topo_matrix)
'''


def recursive_design_generation(state: np.array, origin: np.array, phase: int):
    # input:
    # a) state: a 3-dimensional array that represents the RHS of the design.
    # The LHS should be a mirrored image of the RHS.
    # The size of the array determines the size of the design
    # The zero entries mean non-occupied grid places, one-valued entries mean fuselages,
    # two-valued entries mean wings, 3-valued entries mean rotors
    # b) origin: is the place of the fuselage, should have the x-axis equal to zero, i.e., origin[0] = 0. Also
    # there should be at least one component with each maximum or minimum in each dimension.
    # The origin determines the symmetry in the design: if origin = [0,0,0],
    # then the fuselage is at the front-center-bottom (in y-x-z coordinates) of design
    # c) phase: (skipping fuselage as we're always going to have a single one for now, 2 means wings, 3 means rotors,
    # we set the order beforehand to break symmetries
    '''
    if phase == 2:
        for x in range():
            return
    '''
    pass


def random_topo_generation(state: np.array, origin: np.array, phase: int):
    # input:
    # a) state: a 3-dimensional array that represents the RHS of the design.
    # The LHS should be a mirrored image of the RHS.
    # The size of the array determines the size of the design
    # The zero entries mean non-occupied grid places, one-valued entries mean fuselages,
    # two-valued entries mean wings, 3-valued entries mean rotors
    # b) origin: is the place of the fuselage, should have the x-axis equal to zero, i.e., origin[0] = 0. Also
    # there should be at least one component with each maximum or minimum in each dimension.
    # The origin determines the symmetry in the design: if origin = [0,0,0],
    # then the fuselage is at the front-center-bottom (in y-x-z coordinates) of design
    # c) phase: (skipping fuselage as we're always going to have a single one for now, 2 means wings, 3 means rotors,
    # we set the order beforehand to break symmetries
    for x in range(state.shape[0]):
        for y in range(state.shape[1]):
            for z in range(state.shape[2]):
                if state[x, y, z] != 0:
                    pass


class RuleBook:

    def __init__(self, rule_dict):
        self.rule_dict = rule_dict

    def apply_rule(self, current_topology: np.array, rule_id: int) -> np.array:
        pass


def node_matches_rule_center(node, state, rule_lhs):
    return state[node[0], node[1], node[2]] == rule_lhs[Neighbors.CENTER]


def node_matches_rule_right(node, state, rule_lhs):
    return not (Neighbors.RIGHT in rule_lhs or (node[0] + 1 < state.shape[0] and
                                                state[node[0] + 1, node[1], node[2]] == rule_lhs[Neighbors.RIGHT]))


def node_matches_rule_left(node, state, rule_lhs):
    return not (Neighbors.LEFT in rule_lhs or (node[0] >= 1 and
                                               state[node[0] - 1, node[1], node[2]] == rule_lhs[Neighbors.LEFT]))


def node_matches_rule_top(node, state, rule_lhs):
    return not (Neighbors.TOP in rule_lhs or (node[2] + 1 < state.shape[2] and
                                              state[node[0], node[1], node[2] + 1] == rule_lhs[Neighbors.TOP]))


def node_matches_rule_bottom(node, state, rule_lhs):
    return not (Neighbors.BOTTOM in rule_lhs or (node[2] >= 1 and
                                                 state[node[0], node[1], node[2] - 1] == rule_lhs[Neighbors.BOTTOM]))


def node_matches_rule_front(node, state, rule_lhs):
    return not (Neighbors.FRONT in rule_lhs or (node[1] + 1 < state.shape[1] and
                                                state[node[0], node[1] + 1, node[2]] == rule_lhs[Neighbors.FRONT]))


def node_matches_rule_rear(node, state, rule_lhs):
    return not (Neighbors.REAR in rule_lhs or (node[1] >= 1 and
                                               state[node[0], node[1] - 1, node[2]] == rule_lhs[Neighbors.REAR]))


def node_matches_rule(node, state, rule_lhs):
    return node_matches_rule_center(node, state, rule_lhs) and node_matches_rule_right(node, state, rule_lhs) and \
           node_matches_rule_left(node, state, rule_lhs) and node_matches_rule_top(node, state, rule_lhs) and \
           node_matches_rule_bottom(node, state, rule_lhs) and node_matches_rule_front(node, state, rule_lhs) and \
           node_matches_rule_rear(node, state, rule_lhs)


def get_matching_rules(node, state, rule_list):
    matching_rules = []
    for rule in rule_list:
        if node_matches_rule(node, state, rule[0]):
            matching_rules.append(rule)
    return matching_rules


def apply_rule(node, state, rule_rhs):
    if Neighbors.CENTER in rule_rhs:
        state[node[0], node[1], node[2]] = rule_rhs[Neighbors.CENTER]
    if Neighbors.RIGHT in rule_rhs:
        state[node[0] + 1, node[1], node[2]] = rule_rhs[Neighbors.RIGHT]
    if Neighbors.LEFT in rule_rhs:
        state[node[0] - 1, node[1], node[2]] = rule_rhs[Neighbors.LEFT]
    if Neighbors.FRONT in rule_rhs:
        state[node[0], node[1] + 1, node[2]] = rule_rhs[Neighbors.FRONT]
    if Neighbors.REAR in rule_rhs:
        state[node[0], node[1] - 1, node[2]] = rule_rhs[Neighbors.REAR]
    if Neighbors.TOP in rule_rhs:
        state[node[0], node[1], node[2] + 1] = rule_rhs[Neighbors.TOP]
    if Neighbors.BOTTOM in rule_rhs:
        state[node[0], node[1], node[2] - 1] = rule_rhs[Neighbors.BOTTOM]
    return state


def get_children(node, state):
    children = []
    if node[0] + 1 <= state.shape[0] and state[node[0] + 1, node[1], node[2]] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.RIGHT)
    if node[0] >= 1 and state[node[0] - 1, node[1], node[2]] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.LEFT)
    if node[1] + 1 <= state.shape[1] and state[node[0], node[1] + 1, node[2]] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.FRONT)
    if node[1] >= 1 and state[node[0], node[1] - 1, node[2]] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.REAR)
    if node[2] + 1 <= state.shape[2] and state[node[0], node[1], node[2] + 1] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.TOP)
    if node[2] >= 1 and state[node[0], node[1], node[2] - 1] == GrammarSymbols.UNOCCUPIED:
        children.append(Neighbors.BOTTOM)
    return children


def reflect_state(state):
    reflected_state = np.zeros((state.shape[0]-1, state.shape[1], state.shape[2]))
    for i in range(state.shape[0] - 1):
        for j in range(state.shape[1]):
            for k in range(state.shape[2]):
                reflected_state[i, j, k] = state[-1 - i, j, k]
    return reflected_state


def concatenate_state(left_state, right_state):
    design_shape = (left_state.shape[0] + right_state.shape[0], left_state.shape[1], left_state.shape[2])
    design = np.zeros(design_shape)
    design[:left_state.shape[0], :, :] = copy.deepcopy(left_state)
    design[left_state.shape[0]:, :, :] = copy.deepcopy(right_state)
    return design


if __name__ == "__main__":

    # center, left, head, right, tail, bottom, top

    rule_list = []
    # add wings
    l_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.RIGHT: GrammarSymbols.UNOCCUPIED}
    r_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.RIGHT: GrammarSymbols.WING}
    rule_list.append([l_state, r_state])

    # add rotor to the right
    l_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.RIGHT: GrammarSymbols.UNOCCUPIED}
    r_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.RIGHT: GrammarSymbols.ROTOR}
    rule_list.append([l_state, r_state])

    # add rotor to the left
    l_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.LEFT: GrammarSymbols.UNOCCUPIED}
    r_state = {Neighbors.CENTER: GrammarSymbols.BODY, Neighbors.LEFT: GrammarSymbols.ROTOR}
    rule_list.append([l_state, r_state])

    # add rotor to the top
    l_state = {Neighbors.CENTER: GrammarSymbols.CONNECTOR, Neighbors.TOP: GrammarSymbols.UNOCCUPIED}
    r_state = {Neighbors.CENTER: GrammarSymbols.CONNECTOR, Neighbors.TOP: GrammarSymbols.ROTOR}
    rule_list.append([l_state, r_state])

    num_designs = 10
    designs = []
    for idx in range(num_designs):
        possible_half_widths = list(range(1, 5))
        possible_lengths = list(range(5))
        possible_depths = list(range(5))
        fuselage_position_y = random.choice(possible_lengths)
        fuselage_position_z = random.choice(possible_depths)
        origin = np.array([0, fuselage_position_y, fuselage_position_z])
        traversal_stack = [origin]
        state = GrammarSymbols.UNOCCUPIED * np.ones((possible_half_widths, possible_lengths, possible_depths))
        while traversal_stack:
            node = traversal_stack.pop()
            if np.all(node == origin):
                state[origin[0], origin[1], origin[2]] = GrammarSymbols.FUSELAGE  # fuselage
            else:
                matching_rules = get_matching_rules(node, state, rule_list)
                rule_to_apply = random.choice(matching_rules)
                state = apply_rule(node, state, rule_to_apply[1])
                children = get_children(node, state)
                traversal_stack.extend(children)

        design = concatenate_state(reflect_state(state), state)
        designs.append(design)
