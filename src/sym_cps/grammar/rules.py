from __future__ import annotations

import copy
import json
import random

from aenum import Enum, auto

import numpy as np


# from sym_cps.shared.objects import grammar_rules


# from igraph import Edge, Graph, Vertex


class GrammarSymbols(Enum):
    UNOCCUPIED = auto()
    ANYTHING = auto()
    BOUNDARY = auto()
    FUSELAGE = auto()
    WING = auto()
    ROTOR = auto()
    BODY = auto()
    HUB = auto()
    TUBE = auto()
    CONNECTOR = auto()
    EMPTY = auto()
    VERT_WING = auto()


class Neighbors(Enum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    FRONT = auto()
    REAR = auto()


# Dictionary connected to the json
# my_rules = grammar_rules


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


def node_matches_rule_center(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if state[node[0]][node[1]][node[2]] in rule_lhs["S"]:
        return True
    for symbol in rule_lhs["S"]:
        if symbol in symbol_groups and state[node[0]][node[1]][node[2]] in symbol_groups[symbol]:
            return True
    return False


def node_matches_rule_right(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "RS" not in rule_lhs:
        return True
    if node[0] + 1 < len(state):
        if state[node[0] + 1][node[1]][node[2]] in rule_lhs["RS"]:
            return True
        for symbol in rule_lhs["RS"]:
            if symbol in symbol_groups and state[node[0] + 1][node[1]][node[2]] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["RS"]:
        return True
    return False
    '''
    return (not Neighbors.RIGHT in rule_lhs) or (node[0] + 1 < len(state) and
                                                 (state[node[0] + 1][node[1]][node[2]] == rule_lhs[Neighbors.RIGHT] or
                                                  (rule_lhs[Neighbors.RIGHT] in symbol_groups and
                                                   state[node[0] + 1][node[1]][node[2]] in symbol_groups[
                                                       rule_lhs[Neighbors.RIGHT]])))
    '''


def node_matches_rule_left(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "LS" not in rule_lhs:
        return True
    if node[0] >= 1:
        if state[node[0] - 1][node[1]][node[2]] in rule_lhs["LS"]:
            return True
        for symbol in rule_lhs["LS"]:
            if symbol in symbol_groups and state[node[0] - 1][node[1]][node[2]] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["LS"]:
        return True
    return False
    '''
    return (not Neighbors.LEFT in rule_lhs) or (node[0] >= 1 and
                                                (state[node[0] - 1][node[1]][node[2]] == rule_lhs[Neighbors.LEFT] or
                                                (rule_lhs[Neighbors.LEFT] in symbol_groups and
                                                 state[node[0] - 1][node[1]][node[2]] in symbol_groups[
                                                     rule_lhs[Neighbors.LEFT]])))
    '''


def node_matches_rule_top(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "T" not in rule_lhs:
        return True
    if node[2] + 1 < len(state[0][0]):
        if state[node[0]][node[1]][node[2] + 1] in rule_lhs["T"]:
            return True
        for symbol in rule_lhs["T"]:
            if symbol in symbol_groups and state[node[0]][node[1]][node[2] + 1] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["T"]:
        return True
    return False
    '''
    return (not Neighbors.TOP in rule_lhs) or (node[2] + 1 < len(state[0][0]) and
                                               (state[node[0]][node[1]][node[2] + 1] == rule_lhs[Neighbors.TOP] or
                                               (rule_lhs[Neighbors.TOP] in symbol_groups and
                                                state[node[0]][node[1]][node[2] + 1] in symbol_groups[
                                                    rule_lhs[Neighbors.TOP]])))
    '''


def node_matches_rule_bottom(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "B" not in rule_lhs:
        return True
    if node[2] >= 1:
        if state[node[0]][node[1]][node[2] - 1] in rule_lhs["B"]:
            return True
        for symbol in rule_lhs["B"]:
            if symbol in symbol_groups and state[node[0]][node[1]][node[2] - 1] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["B"]:
        return True
    return False
    '''
    return (not Neighbors.BOTTOM in rule_lhs) or (node[2] >= 1 and
                                                  (state[node[0]][node[1]][node[2] - 1] == rule_lhs[Neighbors.BOTTOM] or
                                                  (rule_lhs[Neighbors.BOTTOM] in symbol_groups and
                                                   state[node[0]][node[1]][node[2] - 1] in symbol_groups[
                                                       rule_lhs[Neighbors.BOTTOM]])))
    '''


def node_matches_rule_front(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "F" not in rule_lhs:
        return True
    if node[1] < len(state[0]) - 1:
        if state[node[0]][node[1] + 1][node[2]] in rule_lhs["F"]:
            return True
        for symbol in rule_lhs["F"]:
            if symbol in symbol_groups and state[node[0]][node[1] + 1][node[2]] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["F"]:
        return True
    return False
    '''
    return (not Neighbors.FRONT in rule_lhs) or (node[1] + 1 < len(state[0]) and
                                                 (state[node[0]][node[1] + 1][node[2]] == rule_lhs[Neighbors.FRONT] or
                                                 (rule_lhs[Neighbors.FRONT] in symbol_groups and
                                                  state[node[0]][node[1] + 1][node[2]] in symbol_groups[
                                                      rule_lhs[Neighbors.FRONT]])))
    '''


def node_matches_rule_rear(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    rule_lhs = rule["conditions"]
    rule_rhs = rule["production"]
    if "ROTOR" in rule_rhs.values() and not remaining_rotors or "WING" in rule_rhs.values() and not remaining_wings:
        return False
    if "R" not in rule_lhs:
        return True
    if node[1] >= 1:
        if state[node[0]][node[1] - 1][node[2]] in rule_lhs["R"]:
            return True
        for symbol in rule_lhs["R"]:
            if symbol in symbol_groups and state[node[0]][node[1] - 1][node[2]] in symbol_groups[symbol]:
                return True
        return False
    if "BOUNDARY" in rule_lhs["R"]:
        return True
    return False
    '''
    return (not Neighbors.REAR in rule_lhs) or (node[1] >= 1 and
                                                (state[node[0]][node[1] - 1][node[2]] == rule_lhs[Neighbors.REAR] or
                                                 (rule_lhs[Neighbors.REAR] in symbol_groups and
                                                  state[node[0]][node[1] - 1][node[2]] in symbol_groups[
                                                      rule_lhs[Neighbors.REAR]])))
    '''


def node_matches_rule(node, state, rule, symbol_groups, remaining_rotors, remaining_wings):
    return node_matches_rule_center(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_right(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_left(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_top(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_bottom(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_front(node, state, rule, symbol_groups, remaining_rotors, remaining_wings) and \
           node_matches_rule_rear(node, state, rule, symbol_groups, remaining_rotors, remaining_wings)


def get_matching_rules(node, state, rule_dict, symbol_groups, remaining_rotors, remaining_wings):
    matching_rules = []
    for id in rule_dict:
        if node_matches_rule(node, state, rule_dict[id], symbol_groups, remaining_rotors, remaining_wings):
            matching_rules.append(rule_dict[id])
    return matching_rules


def apply_rule(node, state, adjacency_dict, rule_rhs, remaining_rotors, remaining_wings):
    if "S" in rule_rhs:
        state[node[0]][node[1]][node[2]] = rule_rhs["S"]
    if "ROTOR" in rule_rhs["S"]:
        remaining_rotors -= 1
    if "WING" in rule_rhs["S"]:
        remaining_wings -= 1
    '''
    if Neighbors.RIGHT in rule_rhs:
        state[node[0] + 1][node[1]][node[2]] = rule_rhs[Neighbors.RIGHT]
        if rule_rhs[Neighbors.RIGHT] != "EMPTY":
            if (node[0], node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0] + 1, node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0] + 1, node[1], node[2])]
    if Neighbors.LEFT in rule_rhs:
        state[node[0] - 1][node[1]][node[2]] = rule_rhs[Neighbors.LEFT]
        if rule_rhs[Neighbors.LEFT] != "EMPTY":
            if (node[0], node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0] - 1, node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0] - 1, node[1], node[2])]
    if Neighbors.FRONT in rule_rhs:
        state[node[0]][node[1] + 1][node[2]] = rule_rhs[Neighbors.FRONT]
        if rule_rhs[Neighbors.FRONT] != "EMPTY":
            if (node[0], node[1] + 1, node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0], node[1] + 1, node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0], node[1] + 1, node[2])]
    if Neighbors.REAR in rule_rhs:
        state[node[0]][node[1] - 1][node[2]] = rule_rhs[Neighbors.REAR]
        if rule_rhs[Neighbors.REAR] != "EMPTY":
            if (node[0], node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0], node[1] - 1, node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0], node[1] - 1, node[2])]
    if Neighbors.TOP in rule_rhs:
        state[node[0]][node[1]][node[2] + 1] = rule_rhs[Neighbors.TOP]
        if rule_rhs[Neighbors.TOP] != "EMPTY":
            if (node[0], node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0], node[1], node[2] + 1))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0], node[1], node[2] + 1)]
    if Neighbors.BOTTOM in rule_rhs:
        state[node[0]][node[1]][node[2] - 1] = rule_rhs[Neighbors.BOTTOM]
        if rule_rhs[Neighbors.BOTTOM] != "EMPTY":
            if (node[0], node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2])].append((node[0], node[1], node[2] - 1))
            else:
                adjacency_dict[(node[0], node[1], node[2])] = [(node[0], node[1], node[2] - 1)]
    '''
    if "EDGES" in rule_rhs:
        if "LS" in rule_rhs["EDGES"]:
            if (node[0] - 1, node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0] - 1, node[1], node[2])].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0] - 1, node[1], node[2])] = [(node[0], node[1], node[2])]
        if "RS" in rule_rhs["EDGES"]:
            if (node[0] + 1, node[1], node[2]) in adjacency_dict:
                adjacency_dict[(node[0] + 1, node[1], node[2])].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0] + 1, node[1], node[2])] = [(node[0], node[1], node[2])]
        if "F" in rule_rhs["EDGES"]:
            if (node[0], node[1] + 1, node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1] + 1, node[2])].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1] + 1, node[2])] = [(node[0], node[1], node[2])]
        if "R" in rule_rhs["EDGES"]:
            if (node[0], node[1] - 1, node[2]) in adjacency_dict:
                adjacency_dict[(node[0], node[1] - 1, node[2])].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1] - 1, node[2])] = [(node[0], node[1], node[2])]
        if "T" in rule_rhs["EDGES"]:
            if (node[0], node[1], node[2] + 1) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2] + 1)].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2] + 1)] = [(node[0], node[1], node[2])]
        if "B" in rule_rhs["EDGES"]:
            if (node[0], node[1], node[2] - 1) in adjacency_dict:
                adjacency_dict[(node[0], node[1], node[2] - 1)].append((node[0], node[1], node[2]))
            else:
                adjacency_dict[(node[0], node[1], node[2] - 1)] = [(node[0], node[1], node[2])]
    return state, adjacency_dict, remaining_rotors, remaining_wings


def get_children(node, state, adjacency_dict):
    children = []
    if tuple(node) in adjacency_dict:
        for child in adjacency_dict[tuple(node)]:
            if state[child[0]][child[1]][child[2]] != "EMPTY" and \
                    state[child[0]][child[1]][child[2]] != "UNOCCUPIED":
                children.append(tuple(child))
            elif state[child[0]][child[1]][child[2]] == "UNOCCUPIED" and node not in children:
                children.append(node)
    else:
        if node[0] + 1 < len(state) and state[node[0] + 1][node[1]][node[2]] == "UNOCCUPIED":
            children.append((node[0] + 1, node[1], node[2]))
        if node[0] >= 1 and state[node[0] - 1][node[1]][node[2]] == "UNOCCUPIED":
            children.append((node[0] - 1, node[1], node[2]))
        if node[1] + 1 < len(state[0]) and state[node[0]][node[1] + 1][node[2]] == "UNOCCUPIED":
            children.append((node[0], node[1] + 1, node[2]))
        if node[1] >= 1 and state[node[0]][node[1] - 1][node[2]] == "UNOCCUPIED":
            children.append((node[0], node[1] - 1, node[2]))
        if node[2] + 1 < len(state[0][0]) and state[node[0]][node[1]][node[2] + 1] == "UNOCCUPIED":
            children.append((node[0], node[1], node[2] + 1))
        if node[2] >= 1 and state[node[0]][node[1]][node[2] - 1] == "UNOCCUPIED":
            children.append((node[0], node[1], node[2] - 1))
        if children:
            children.append((node[0], node[1], node[2]))
    return children


def trim_loose_ends(state, adjacency_dict):
    progress = True
    while progress:
        progress = False
        for i in range(len(state)):
            for j in range(len(state[0])):
                for k in range(len(state[0][0])):
                    remove_connector = False
                    if state[i][j][k] == "CONNECTOR":
                        remove_connector = True
                        if (i, j, k) in adjacency_dict:
                            for child in adjacency_dict[(i, j, k)]:
                                if state[child[0]][child[1]][child[2]] not in symbol_groups["FREE"]:
                                    remove_connector = False
                                    break
                    if remove_connector or state[i][j][k] == "UNOCCUPIED" or state[i][j][k] == "EMPTY":
                        state[i][j][k] = ""
                        if (i, j, k) in adjacency_dict:
                            del adjacency_dict[(i,j,k)]
                        progress = True
    return state, adjacency_dict



def reflect_state_and_edges(state, adjacency_dict):
    reflected_state = []  # np.zeros((len(state) - 1, len(state[0]), len(state[0][0])))
    for i in range(len(state) - 1):
        reflected_state.append([])
        for j in range(len(state[0])):
            reflected_state[-1].append([])
            for k in range(len(state[0][0])):
                reflected_state[i][j].append(state[-1 - i][j][k])
    left_adjacency_dict = {}
    for key in adjacency_dict:
        if key[0] > 0:
            left_adjacency_dict[(len(state) - 1 - key[0], key[1], key[2])] = []
            for neighbor in adjacency_dict[key]:
                left_adjacency_dict[(len(state) - 1 - key[0], key[1], key[2])].append((len(state) - 1 - neighbor[0],
                                                                                       neighbor[1], neighbor[2]))
    return reflected_state, left_adjacency_dict


def concatenate_state_and_edges(left_state, right_state, left_adjacency_dict, right_adjacency_dict):
    design_shape = (len(left_state) + len(right_state), len(left_state[0]), len(left_state[0][0]))
    design = []
    for i in range(design_shape[0]):
        design.append([])
        for j in range(len(state[0])):
            design[-1].append([])
            for k in range(len(state[0][0])):
                if i < len(left_state):
                    design[i][j].append(left_state[i][j][k])
                else:
                    design[i][j].append(right_state[i - len(left_state)][j][k])
    # design = np.zeros(design_shape)
    # design[:left_state.shape[0], :, :] = copy.deepcopy(left_state)
    # design[left_state.shape[0]:, :, :] = copy.deepcopy(right_state)
    joint_adjacency_dict = copy.deepcopy(left_adjacency_dict)
    for key in right_adjacency_dict:
        joint_adjacency_dict[(key[0] + len(left_state), key[1], key[2])] = []
        for neighbor in right_adjacency_dict[key]:
            joint_adjacency_dict[(key[0] + len(left_state), key[1], key[2])].append(
                (neighbor[0] + len(left_state), neighbor[1], neighbor[2]))
            if key[0] == 0 and neighbor[0] > 0:  # these are the edges going from the center
                joint_adjacency_dict[(len(left_state), key[1], key[2])].append(
                    (len(left_state) - neighbor[0], neighbor[1], neighbor[2]))

    return design, joint_adjacency_dict


def components_count(design):
    # this can be extended to include more conditions for rejecting undesired designs
    num_wings = 0
    num_rotors = 0
    num_fuselage = 0
    for i in range(len(design)):
        for j in range(len(design[0])):
            for k in range(len(design[0][0])):
                if design[i][j][k] == "FUSELAGE":
                    num_fuselage += 1
                elif design[i][j][k] == "ROTOR":
                    num_rotors += 1
                elif design[i][j][k] == "WING":
                    num_wings += 1
    return num_fuselage, num_rotors, num_wings


if __name__ == "__main__":
    '''
    symbol_groups = {GrammarSymbols.BODY: [GrammarSymbols.FUSELAGE,
                                           GrammarSymbols.HUB, GrammarSymbols.TUBE],
                     GrammarSymbols.CONNECTOR: [GrammarSymbols.HUB, GrammarSymbols.TUBE],
                     GrammarSymbols.ANYTHING: [GrammarSymbols.FUSELAGE, GrammarSymbols.HUB, GrammarSymbols.TUBE,
                                               GrammarSymbols.WING, GrammarSymbols.ROTOR, GrammarSymbols.CONNECTOR]}
    '''
    symbol_groups = {"BODY": ["FUSELAGE", "HUB", "TUBE"],
                     "CONNECTOR": ["HUB", "TUBE"],
                     "ANYTHING": ["FUSELAGE", "HUB", "TUBE", "WING", "ROTOR", "CONNECTOR"],
                     "NON-WING": ["FUSELAGE", "HUB", "TUBE", "WING", "ROTOR", "CONNECTOR",
                                  "EMPTY", "UNOCCUPIED", "BOUNDARY"],
                     "FREE": ["UNOCCUPIED", "EMPTY"],
                     "WING-LEFT": ["FUSELAGE", "CONNECTOR", "ROTOR", "WING"],
                     "WING-RIGHT": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "ROTOR", "BOUNDARY"],
                     "WING-TOP": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "WING", "BOUNDARY"],
                     "WING_FRONT": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "ROTOR", "BOUNDARY"]
                     }
    # rule_list = []
    rule_dict_path = "grammar_rules_hussein.json"
    rule_dict = json.load(open(rule_dict_path))
    num_designs = 10
    designs = []
    invalid_designs = []
    for idx in range(num_designs):
        possible_half_widths = random.randint(2, 5)  # list(range(1, 5))
        possible_lengths = random.randint(2, 5)  # list(range(5))
        possible_depths = random.randint(1, 4)
        max_right_num_rotors = random.randint(1, 3)
        max_right_num_wings = random.randint(1, 3)
        remaining_rotors = max_right_num_rotors
        remaining_wings = max_right_num_wings
        fuselage_position_y = random.choice(range(possible_lengths))
        fuselage_position_z = random.choice(range(possible_depths))
        origin = [0, fuselage_position_y, fuselage_position_z]
        traversal_stack = [origin]
        state = []
        for i in range(possible_half_widths):
            state.append([])
            for j in range(possible_lengths):
                state[-1].append([])
                for k in range(possible_depths):
                    state[-1][-1].append("UNOCCUPIED")
                    # np.ones((possible_half_widths, possible_lengths, possible_depths))
        # state[:, :, :] = "UNOCCUPIED"
        adjacency_dict = {}
        while traversal_stack:
            node = traversal_stack.pop()
            if (node[0] == origin[0] or node[1] == origin[1] or node[2] == origin[2]) and \
                    state[origin[0]][origin[1]][origin[2]] == "UNOCCUPIED":
                state[origin[0]][origin[1]][origin[2]] = "FUSELAGE"  # fuselage
            else:
                matching_rules = get_matching_rules(node, state, rule_dict, symbol_groups,
                                                    remaining_rotors, remaining_wings)
                if not matching_rules:
                    continue
                rule_to_apply = random.choice(matching_rules)
                state, adjacency_dict, remaining_rotors, remaining_wings = \
                    apply_rule(node, state, adjacency_dict, rule_to_apply["production"],
                                                   remaining_rotors, remaining_wings)
            children = get_children(node, state, adjacency_dict)
            for child in children:
                if child not in traversal_stack:
                    traversal_stack.append(child)
        state, adjacency_dict = trim_loose_ends(state, adjacency_dict)
        left_state, left_adjacency_dict = reflect_state_and_edges(state, adjacency_dict)
        design, joint_adjacency_dict = concatenate_state_and_edges(left_state, state, left_adjacency_dict,
                                                                   adjacency_dict)
        num_fuselage, num_rotors, num_wings = components_count(design)
        if num_fuselage and num_rotors and num_wings:
            designs.append((design, joint_adjacency_dict, num_fuselage, num_rotors, num_wings))
        else:
            invalid_designs.append((design, joint_adjacency_dict))

    print(np.array(designs))
