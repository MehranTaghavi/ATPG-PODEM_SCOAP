"""
gates.py
Contains logic evaluations and SCOAP controllability formulas for digital gates.
"""
from itertools import product
from src.constants import ValueType

def andGate(inputs: list[ValueType]):
    if all(input == ValueType.One for input in inputs): return ValueType.One
    elif any(input == ValueType.Zero for input in inputs): return ValueType.Zero
    else: return ValueType.Unknown

def orGate(inputs: list[ValueType]):
    if any(input == ValueType.One for input in inputs): return ValueType.One
    elif all(input == ValueType.Zero for input in inputs): return ValueType.Zero
    else: return ValueType.Unknown

def nandGate(inputs: list[ValueType]):
    if all(input == ValueType.One for input in inputs): return ValueType.Zero
    elif any(input == ValueType.Zero for input in inputs): return ValueType.One
    else: return ValueType.Unknown

def norGate(inputs: list[ValueType]):
    if any(input == ValueType.One for input in inputs): return ValueType.Zero
    elif all(input == ValueType.Zero for input in inputs): return ValueType.One
    else: return ValueType.Unknown

def xorGate(inputs: list[ValueType]):
    if any(input == ValueType.Unknown for input in inputs): return ValueType.Unknown
    else: return ValueType.One if inputs.count(ValueType.One) % 2 == 1 else ValueType.Zero

def xnorGate(inputs: list[ValueType]):
    if any(input == ValueType.Unknown for input in inputs): return ValueType.Unknown
    else: return ValueType.Zero if inputs.count(ValueType.One) % 2 == 1 else ValueType.One

def notGate(inputs: list[ValueType]):
    if inputs[0] == ValueType.One: return ValueType.Zero
    elif inputs[0] == ValueType.Zero: return ValueType.One
    else: return ValueType.Unknown

def buffGate(inputs: list[ValueType]):
    return inputs[0]

def andGateControllability(inputsControllabilities: list[list[int]]) -> list[int]:
    return [min([ic[0] for ic in inputsControllabilities]) + 1,
            sum([ic[1] for ic in inputsControllabilities]) + 1]

def orGateControllability(inputsControllabilities: list[list[int]]) -> list[int]:
    return [sum([ic[0] for ic in inputsControllabilities]) + 1,
            min([ic[1] for ic in inputsControllabilities]) + 1]

def nandGateControllability(inputsControllabilities: list[list[int]]) -> list[int]:
    return [sum([ic[1] for ic in inputsControllabilities]) + 1,
            min([ic[0] for ic in inputsControllabilities]) + 1]

def norGateControllability(inputsControllabilities: list[list[int]]) -> list[int]:
    return [min([ic[1] for ic in inputsControllabilities]) + 1,
            sum([ic[0] for ic in inputsControllabilities]) + 1]

def xorGateControllability(inputs_controllabilities: list[list[int]]) -> list[int]:
    inputs_num = len(inputs_controllabilities)
    possible_state1 = []
    possible_state0 = []
    states = list(product([0, 1], repeat=inputs_num))
    states1 = [state for state in states if sum(state) % 2 == 1]
    states0 = [state for state in states if sum(state) % 2 == 0]
    
    for state in states1:
        controllability = sum([inputs_controllabilities[i][state[i]] for i in range(inputs_num)])
        possible_state1.append(controllability)
    for state in states0:
        controllability = sum([inputs_controllabilities[i][state[i]] for i in range(inputs_num)])
        possible_state0.append(controllability)
        
    return [min(possible_state0) + 1, min(possible_state1) + 1]

def xnorGateControllability(inputs_controllabilities: list[list[int]]) -> list[int]:
    inputs_num = len(inputs_controllabilities)
    possible_state1 = []
    possible_state0 = []
    states = list(product([0, 1], repeat=inputs_num))
    states1 = [state for state in states if sum(state) % 2 == 0]
    states0 = [state for state in states if sum(state) % 2 == 1]
    
    for state in states1:
        controllability = sum([inputs_controllabilities[i][state[i]] for i in range(inputs_num)])
        possible_state1.append(controllability)
    for state in states0:
        controllability = sum([inputs_controllabilities[i][state[i]] for i in range(inputs_num)])
        possible_state0.append(controllability)
        
    return [min(possible_state0) + 1, min(possible_state1) + 1]

def notGateControllability(input_controllabilities: list[list[int]]) -> list[int]:
    return [input_controllabilities[1] + 1, input_controllabilities[0] + 1]

def bufGateControllability(input_controllabilities: list[list[int]]) -> list[int]:
    return [input_controllabilities[0] + 1, input_controllabilities[1] + 1]

def register_all_gates(testability_obj):
    testability_obj.addOperation("and", andGate)
    testability_obj.addOperation("or", orGate)
    testability_obj.addOperation("nand", nandGate)
    testability_obj.addOperation("nor", norGate)
    testability_obj.addOperation("xor", xorGate)
    testability_obj.addOperation("xnor", xnorGate)
    testability_obj.addOperation("not", notGate)
    testability_obj.addOperation("buff", buffGate)
    testability_obj.addOperation("buf", buffGate)

    testability_obj.addOperation("andCtrl", andGateControllability)
    testability_obj.addOperation("orCtrl", orGateControllability)
    testability_obj.addOperation("nandCtrl", nandGateControllability)
    testability_obj.addOperation("norCtrl", norGateControllability)
    testability_obj.addOperation("xorCtrl", xorGateControllability)
    testability_obj.addOperation("xnorCtrl", xnorGateControllability)
    testability_obj.addOperation("notCtrl", notGateControllability)
    testability_obj.addOperation("buffCtrl", bufGateControllability)
    testability_obj.addOperation("bufCtrl", bufGateControllability)