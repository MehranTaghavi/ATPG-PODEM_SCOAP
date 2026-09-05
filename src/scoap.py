"""
scoap.py
Handles SCOAP calculations (Controllability and Observability) and Netlist parsing.
"""
import math
from src.constants import ValueType, FaultType

class Testability:
    def __init__(self):
        self.operations = {}
        self.CC_CO = {}

    def addOperation(self, name: str, operation):
        self.operations[name] = operation

    def getValue(self, operation_name: str, inputs: list[ValueType]):
        operation = self.operations.get(operation_name)
        return operation(inputs)

    def calculateControllability(self, netList: dict):
        for net in netList:
            thisNetList = netList[net]
            gateType = thisNetList[2]
            
            if gateType == "inpt":
                self.CC_CO[net] = {"CC": [1, 1]}
            elif gateType == "from":
                stem_net = thisNetList[3].replace("gat", "")
                self.CC_CO[net] = {"CC": [self.CC_CO[stem_net]["CC"][0],
                                          self.CC_CO[stem_net]["CC"][1]]}
            else:
                inputNets = self.getInputNets(thisNetList=thisNetList)
                if gateType in ["not", "buff", "buf"]:
                    inputControllabilities = self.getInputsControllabilities(inputNets=inputNets)[0]
                else:
                    inputControllabilities = self.getInputsControllabilities(inputNets=inputNets)
                
                operation = self.operations.get(f"{gateType}Ctrl")
                self.CC_CO[net] = {"CC": operation(inputControllabilities)}

    def getInputNets(self, thisNetList: list) -> list:
        if thisNetList[2] in ("not", "buf", "buff"):
            return [thisNetList[len(thisNetList) - 2]]
        else:
            inputStartIndex = len(thisNetList) - 1 - int(thisNetList[4])
            inputEndIndex = len(thisNetList) - 1
            return thisNetList[inputStartIndex: inputEndIndex]

    def getInputsControllabilities(self, inputNets: list) -> list:
        return [self.CC_CO[input_net]["CC"] for input_net in inputNets]

    def reverseNetList(self, netList: dict) -> dict:
        return dict(reversed(list(netList.items())))

    def calculateObservability(self, netList: dict):
        reversedNetList = self.reverseNetList(netList)
        for net in self.CC_CO:
            self.CC_CO[net]["CO"] = math.inf
            
        for net, thisNetList in reversedNetList.items():
            if thisNetList[3] == "0":
                self.CC_CO[net]["CO"] = 0
                
            if thisNetList[2] == "from":
                fanoutStemName = thisNetList[3].replace("gat", "")
                netListKeys = list(netList.keys())
                fanoutCount = int(netList[fanoutStemName][3])
                fanoutBranchRangeStartIndex = netListKeys.index(fanoutStemName) + 1
                fanoutBranchRangeEndIndex = fanoutBranchRangeStartIndex + fanoutCount
                
                self.CC_CO[fanoutStemName]["CO"] = min(
                    [self.CC_CO[branch]["CO"] for branch in netListKeys[fanoutBranchRangeStartIndex:fanoutBranchRangeEndIndex]]
                ) + 1
                continue
                
            inputStartIndex = len(thisNetList) - 1 - int(thisNetList[4])
            inputEndIndex = len(thisNetList) - 1
            inputs = thisNetList[inputStartIndex: inputEndIndex]
            gateType = thisNetList[2]
            self.assignGateInputsObservabilities(gateType, inputs, net)

    def assignGateInputsObservabilities(self, gateType: str, inputs: list, net: str):
        if len(inputs) == 1:
            self.CC_CO[inputs[0]]["CO"] = self.CC_CO[net]["CO"] + 1
            return
            
        for i in inputs:
            self.CC_CO[i]["CO"] = self.CC_CO[net]["CO"] + 1
            for j in inputs:
                if i == j:
                    continue
                if gateType in ["nand", "and"]:
                    self.CC_CO[i]["CO"] += self.CC_CO[j]["CC"][1]
                elif gateType in ["or", "nor"]:
                    self.CC_CO[i]["CO"] += self.CC_CO[j]["CC"][0]
                elif gateType in ["xor", "xnor"]:
                    self.CC_CO[i]["CO"] += min(self.CC_CO[j]["CC"])

    def readISC(self, file) -> dict:
        netlist = {}
        isInputsLine = False
        lastNet = None
        for line in file.readlines():
            if line.startswith('*'):
                continue
            tmp = line.strip().split()
            if isInputsLine:
                tmp = netlist[lastNet] + tmp
                tmp.append(ValueType.Unknown)
                isInputsLine = False
            elif tmp[2] == "inpt" or tmp[2] == "from":
                tmp.append(ValueType.Unknown)
            else:
                isInputsLine = True
                lastNet = tmp[0]
            netlist[tmp[0]] = tmp
        return netlist

    def readFaults(self, file, netList) -> list:
        file.seek(0)
        faultList = []
        for line in file.readlines():
            tmp = line.strip().split()
            if "_" in tmp[0]:
                j = -1
                lastDigit = tmp[0][-1]
                currentNumber = lastDigit
                while tmp[0][j] != "_":
                    if tmp[0][j - 1] != "_":
                        currentDigit = tmp[0][j - 1]
                        currentNumber = currentDigit + currentNumber
                        j -= 1
                    else:
                        break
                tmp[0] = tmp[0].replace(f"_{currentNumber}", "gat")
                k = 1
                for net in netList:
                    if netList[net][2] == "from" and netList[net][3] == tmp[0]:
                        if k == int(currentNumber):
                            tmp[0] = net
                            break
                        k += 1
            faultList.append((tmp[0], FaultType.SA0 if tmp[1] == "sa0" else FaultType.SA1))
        return faultList