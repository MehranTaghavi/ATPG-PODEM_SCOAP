"""Four-valued logic operations used by the phase-one analyses."""

from enum import Enum


class ValueType(Enum):
    One = "1"
    Zero = "0"
    Unknown = "U"
    HighZ = "Z"


def and_gate(inputs: list[ValueType]) -> ValueType:
    if all(value == ValueType.One for value in inputs):
        return ValueType.One
    if any(value == ValueType.Zero for value in inputs):
        return ValueType.Zero
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.HighZ


def or_gate(inputs: list[ValueType]) -> ValueType:
    if any(value == ValueType.One for value in inputs):
        return ValueType.One
    if all(value == ValueType.Zero for value in inputs):
        return ValueType.Zero
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.HighZ


def nand_gate(inputs: list[ValueType]) -> ValueType:
    if all(value == ValueType.One for value in inputs):
        return ValueType.Zero
    if any(value == ValueType.Zero for value in inputs):
        return ValueType.One
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.HighZ


def nor_gate(inputs: list[ValueType]) -> ValueType:
    if any(value == ValueType.One for value in inputs):
        return ValueType.Zero
    if all(value == ValueType.Zero for value in inputs):
        return ValueType.One
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.HighZ


def xor_gate(inputs: list[ValueType]) -> ValueType:
    if ValueType.HighZ in inputs:
        return ValueType.HighZ
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.One if inputs.count(ValueType.One) % 2 else ValueType.Zero


def xnor_gate(inputs: list[ValueType]) -> ValueType:
    if ValueType.HighZ in inputs:
        return ValueType.HighZ
    if ValueType.Unknown in inputs:
        return ValueType.Unknown
    return ValueType.Zero if inputs.count(ValueType.One) % 2 else ValueType.One


def not_gate(inputs: list[ValueType]) -> ValueType:
    if inputs[0] == ValueType.HighZ:
        return ValueType.HighZ
    if inputs[0] == ValueType.One:
        return ValueType.Zero
    if inputs[0] == ValueType.Zero:
        return ValueType.One
    return ValueType.Unknown


def buff_gate(inputs: list[ValueType]) -> ValueType:
    return inputs[0]


def register_logic_operations(testability) -> None:
    operations = {
        "and": and_gate,
        "or": or_gate,
        "nand": nand_gate,
        "nor": nor_gate,
        "xor": xor_gate,
        "xnor": xnor_gate,
        "not": not_gate,
        "buff": buff_gate,
        "buf": buff_gate,
    }
    for name, operation in operations.items():
        testability.addOperation(name, operation)
