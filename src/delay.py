"""Timing-aware testability propagation for phase one."""

import copy
import re

from src.four_valued_logic import ValueType, register_logic_operations


class DelayTestability:
    def __init__(self) -> None:
        self.operations = {}
        register_logic_operations(self)

    def addOperation(self, name: str, operation) -> None:
        self.operations[name] = operation

    def getValue(self, operation_name: str, inputs: list[ValueType]) -> ValueType:
        return self.operations[operation_name](inputs)

    def readISC(self, file) -> dict:
        netlist = {}
        is_inputs_line = False
        last_net = None
        for line in file.readlines():
            if line.startswith("*"):
                continue
            values = [value for value in re.split(r"\W+", line) if value]
            if is_inputs_line:
                values = netlist[last_net] + values
                values.append({-1: ValueType.Unknown})
                is_inputs_line = False
            elif values[2] in ("inpt", "from"):
                values.append({-1: ValueType.Unknown})
            else:
                is_inputs_line = True
                last_net = values[0]
            netlist[values[0]] = values
        return netlist

    def readInputFile(self, file, count: int) -> tuple[dict, list[int]]:
        header = file.readline().strip().split()
        wire_names = [header[0].replace("Input:", "")] + header[1:-1]
        wire_values = {wire: [] for wire in wire_names}
        time_values = []
        for _ in range(count):
            line = file.readline()
            if line:
                values = line.strip().split()
                time_values.append(int(values[-1]))
                for wire_name, value in zip(wire_names, values[:-1]):
                    wire_values[wire_name].append(ValueType(value))
            else:
                for wire_name in wire_names:
                    wire_values[wire_name].append(wire_values[wire_name][-1])
        return wire_values, time_values

    def initialValue(self, netlist: dict, input_values: dict, time: int) -> None:
        for name, value in input_values.items():
            net = netlist[name]
            if net[2] == "inpt":
                net[-1][time] = value

    def assignAllValues(self, netlist: dict, time: int) -> None:
        for net in netlist.values():
            if net[2] == "inpt":
                continue
            if net[2] == "from":
                for source in netlist.values():
                    if source[1] == net[3]:
                        net[-1][time] = source[-1].get(time, ValueType.Unknown)
                        break
                continue
            start = len(net) - 2 - int(net[4])
            input_nets = [netlist[name] for name in net[start:-2]]
            input_values = [input_net[-1].get(time, ValueType.Unknown) for input_net in input_nets]
            net[-1][time + int(net[-2])] = self.getValue(net[2], input_values)

    def calculateMaxTime(self, netlist: dict) -> int:
        output_delays = []
        for net in netlist.values():
            if net[2] in ("inpt", "from"):
                continue
            start = len(net) - 2 - int(net[4])
            input_nets = [netlist[name] for name in net[start:-2]]
            input_delays = []
            for input_net in input_nets:
                if input_net[2] == "inpt":
                    input_delays.append(0)
                elif input_net[2] == "from":
                    source = netlist[input_net[3].replace("gat", "")]
                    input_delays.append(0 if source[2] == "inpt" else int(source[-2]))
                else:
                    input_delays.append(int(input_net[-2]))
            net[-2] = int(net[-2]) + max(input_delays, default=0)
            if net[3] == "0":
                output_delays.append(int(net[-2]))
        return max(output_delays)


def export_delay_values(input_path: str, isc_path: str, output_path: str) -> None:
    testability = DelayTestability()
    with open(input_path, "r") as input_file, open(isc_path, "r") as isc_file:
        netlist = testability.readISC(isc_file)
        max_delay = testability.calculateMaxTime(copy.deepcopy(netlist))
        input_lines = input_file.readlines()
        max_input_time = int(input_lines[-1].strip().split()[-1])
        max_time = max_input_time + max_delay + 1
        input_file.seek(0)
        wire_values, time_values = testability.readInputFile(input_file, max_time)
        with open(output_path, "w") as output_file:
            output_file.write("Node\tValue\n")
            for time in range(max_time):
                last_input_time = time_values[-1]
                input_index = last_input_time if time > last_input_time else time
                input_values = {name: values[input_index] for name, values in wire_values.items()}
                testability.initialValue(netlist, input_values, time)
                testability.assignAllValues(netlist, time)
                output_file.write(f"Time: {time}\n" + "*" * 50 + "\n")
                for net in netlist.values():
                    value = net[-1].get(time, ValueType.Unknown)
                    output_file.write(f"{net[0]}\t\t{value.value}\n")
                output_file.write("\n")
