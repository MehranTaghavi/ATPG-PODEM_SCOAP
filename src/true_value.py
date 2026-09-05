"""Combinational true-value propagation for phase one."""

from src.four_valued_logic import ValueType, register_logic_operations


class TrueValueTestability:
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
            values = line.strip().split()
            if is_inputs_line:
                values = netlist[last_net] + values
                values.append(ValueType.Unknown)
                is_inputs_line = False
            elif values[2] in ("inpt", "from"):
                values.append(ValueType.Unknown)
            else:
                is_inputs_line = True
                last_net = values[0]
            netlist[values[0]] = values
        return netlist

    def readInputFile(self, file) -> tuple[dict, list[int]]:
        header = file.readline().strip().split()
        wire_names = [header[0].replace("Input:", "")] + header[1:-1]
        wire_values = {wire: [] for wire in wire_names}
        time_values = []
        for line in file.readlines():
            values = line.strip().split()
            time_values.append(int(values[-1]))
            for wire_name, value in zip(wire_names, values[:-1]):
                wire_values[wire_name].append(ValueType(value))
        return wire_values, time_values

    def initialValue(self, netlist: dict, input_values: dict) -> None:
        for name, value in input_values.items():
            net = netlist[name]
            if net[2] == "inpt":
                net[-1] = value

    def assignAllValues(self, netlist: dict) -> None:
        for net in netlist.values():
            if net[2] == "inpt":
                continue
            if net[2] == "from":
                for source in netlist.values():
                    if source[1] == net[3]:
                        net[-1] = source[-1]
                        break
                continue
            start = len(net) - 1 - int(net[4])
            inputs = [netlist[name] for name in net[start:-1]]
            net[-1] = self.getValue(net[2], [input_net[-1] for input_net in inputs])


def export_true_values(input_path: str, isc_path: str, output_path: str) -> None:
    testability = TrueValueTestability()
    with open(input_path, "r") as input_file, open(isc_path, "r") as isc_file:
        netlist = testability.readISC(isc_file)
        wire_values, time_values = testability.readInputFile(input_file)
        with open(output_path, "w") as output_file:
            for index, time in enumerate(time_values):
                testability.initialValue(
                    netlist,
                    {name: values[index] for name, values in wire_values.items()},
                )
                testability.assignAllValues(netlist)
                output_file.write(f"Time: {time}\n" + "*" * 50 + "\n")
                for net in netlist.values():
                    output_file.write(f"{net[0]}\t\t{net[-1].value}\n")
                output_file.write("\n")
