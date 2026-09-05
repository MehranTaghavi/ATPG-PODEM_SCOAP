"""
podem.py
Implements the Path-Oriented Decision Making (PODEM) algorithm for ATPG.
"""
import math
from src.constants import ValueType, FaultType
from src.scoap import Testability

class PODEM:
    def __init__(self, testabilityObj: Testability):
        self.testabilityObj = testabilityObj

    def clearNetList(self, netList: dict):
        for i in netList.keys():
            netList[i][-1] = ValueType.Unknown

    def xpathCheck(self, netList: dict, fault: tuple) -> bool:
        faultyNet = netList[fault[0]]
        faultyNets = [faultyNet]
        
        for i in netList.keys():
            net = netList[i]
            if net[2] == "from":
                if net[3] in [fnet[1] for fnet in faultyNets]:
                    faultyNets.append(net)
            elif net[2] == "inpt":
                continue
            else:
                startInputsIndex = len(net) - 1 - int(net[4])
                endInputsIndex = len(net) - 1
                if any([(fnet[0] in net[startInputsIndex:endInputsIndex]) for fnet in faultyNets]):
                    inputNets = [netList[j] for j in net[startInputsIndex: endInputsIndex]]
                    inputValues = [inputNet[-1] for inputNet in inputNets]
                    
                    if self.getValueIn5(net[2], inputValues) in (ValueType.Unknown, ValueType.One_Zero, ValueType.Zero_One):
                        faultyNets.append(net)
                        
            if faultyNets[-1][2] != "from" and faultyNets[-1][3] == "0":
                return True
        return False

    def obtainObjective(self, netList: dict, fault: tuple, controllabilies: dict) -> list:
        faultyNet = netList[fault[0]]
        
        if faultyNet[-1] == ValueType.Unknown:
            return [fault[0], ValueType.One if fault[1] == FaultType.SA0 else ValueType.Zero]
        
        keys = list(netList.keys())
        for i in range(len(keys) - 1, -1, -1):
            net = netList[keys[i]]
            if net[-1] != ValueType.Unknown or net[2] in ["from", "inpt"]:
                continue
                
            startInputsIndex = len(net) - 1 - int(net[4])
            endInputsIndex = len(net) - 1
            inputNets = [netList[j] for j in net[startInputsIndex: endInputsIndex]]
            inputValues = [inputNet[-1] for inputNet in inputNets]
            
            isDfrontier = any(val in [ValueType.One_Zero, ValueType.Zero_One] for val in inputValues)
            if not isDfrontier:
                continue
                
            minControlNetIndex = [None, None]
            minControlValue = [math.inf, math.inf]
            
            for j, inputNet in enumerate(inputNets):
                if inputNet[-1] == ValueType.Unknown:
                    netControl = controllabilies[inputNet[0]]["CC"]
                    if netControl[0] < minControlValue[0]:
                        minControlValue[0], minControlNetIndex[0] = netControl[0], j
                    if netControl[1] < minControlValue[1]:
                        minControlValue[1], minControlNetIndex[1] = netControl[1], j
                        
            if minControlValue[0] < minControlValue[1]:
                inputValues[minControlNetIndex[0]] = ValueType.Zero
                if self.getValueIn5(net[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                    return [inputNets[minControlNetIndex[0]][0], ValueType.Zero]
                else:
                    inputValues[minControlNetIndex[0]] = ValueType.Unknown
                    inputValues[minControlNetIndex[1]] = ValueType.One
                    if self.getValueIn5(net[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                        return [inputNets[minControlNetIndex[1]][0], ValueType.One]
            else:
                inputValues[minControlNetIndex[1]] = ValueType.One
                if self.getValueIn5(net[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                    return [inputNets[minControlNetIndex[1]][0], ValueType.One]
                else:
                    inputValues[minControlNetIndex[1]] = ValueType.Unknown
                    inputValues[minControlNetIndex[0]] = ValueType.Zero
                    if self.getValueIn5(net[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                        return [inputNets[minControlNetIndex[0]][0], ValueType.Zero]

    def backTrace(self, netList: dict, objective: list, controllabilies: dict) -> list:
        objectiveNet = netList[objective[0]]
        objectiveValue = objective[1]
        
        while True:
            if objectiveNet[2] == "inpt":
                return [objectiveNet[0], objectiveValue]
            elif objectiveNet[2] == "from":
                for i in netList.keys():
                    if netList[i][1] == objectiveNet[3]:
                        objectiveNet = netList[i]
                        break
            else:
                startInputsIndex = len(objectiveNet) - 1 - int(objectiveNet[4])
                endInputsIndex = len(objectiveNet) - 1
                inputNets = [netList[j] for j in objectiveNet[startInputsIndex: endInputsIndex]]
                inputValues = [inputNet[-1] for inputNet in inputNets]
                
                minControlNetIndex, minControlValue = [None, None], [math.inf, math.inf]
                maxControlNetIndex, maxControlValue = [None, None], [0, 0]
                
                for j, inputNet in enumerate(inputNets):
                    if inputNet[-1] == ValueType.Unknown:
                        netControl = controllabilies[inputNet[0]]["CC"]
                        if netControl[0] < minControlValue[0]:
                            minControlValue[0], minControlNetIndex[0] = netControl[0], j
                        if netControl[1] < minControlValue[1]:
                            minControlValue[1], minControlNetIndex[1] = netControl[1], j
                        if netControl[0] > maxControlValue[0]:
                            maxControlValue[0], maxControlNetIndex[0] = netControl[0], j
                        if netControl[1] > maxControlValue[1]:
                            maxControlValue[1], maxControlNetIndex[1] = netControl[1], j
                            
                assignObjective = False
                
                if minControlValue[0] < minControlValue[1]:
                    inputValues[minControlNetIndex[0]] = ValueType.Zero
                    if self.getValueIn5(objectiveNet[2], inputValues) == objectiveValue:
                        objectiveNet, objectiveValue, assignObjective = inputNets[minControlNetIndex[0]], ValueType.Zero, True
                    inputValues[minControlNetIndex[0]] = ValueType.Unknown
                    
                if not assignObjective:
                    inputValues[minControlNetIndex[1]] = ValueType.One
                    if self.getValueIn5(objectiveNet[2], inputValues) == objectiveValue:
                        objectiveNet, objectiveValue, assignObjective = inputNets[minControlNetIndex[1]], ValueType.One, True
                    inputValues[minControlNetIndex[1]] = ValueType.Unknown
                    
                if not assignObjective:
                    inputValues[minControlNetIndex[0]] = ValueType.Zero
                    if self.getValueIn5(objectiveNet[2], inputValues) == objectiveValue:
                        objectiveNet, objectiveValue, assignObjective = inputNets[minControlNetIndex[0]], ValueType.Zero, True
                    inputValues[minControlNetIndex[0]] = ValueType.Unknown
                    
                if not assignObjective:
                    if maxControlValue[0] > maxControlValue[1]:
                        inputValues[maxControlNetIndex[0]] = ValueType.Zero
                        if self.getValueIn5(objectiveNet[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                            objectiveNet, objectiveValue, assignObjective = inputNets[maxControlNetIndex[0]], ValueType.Zero, True
                        inputValues[maxControlNetIndex[0]] = ValueType.Unknown
                    if not assignObjective:
                        inputValues[maxControlNetIndex[1]] = ValueType.One
                        if self.getValueIn5(objectiveNet[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                            objectiveNet, objectiveValue, assignObjective = inputNets[maxControlNetIndex[1]], ValueType.One, True
                        inputValues[maxControlNetIndex[1]] = ValueType.Unknown
                    if not assignObjective:
                        inputValues[maxControlNetIndex[0]] = ValueType.Zero
                        if self.getValueIn5(objectiveNet[2], inputValues) in (ValueType.Unknown, ValueType.Zero_One, ValueType.One_Zero):
                            objectiveNet, objectiveValue, assignObjective = inputNets[maxControlNetIndex[0]], ValueType.Zero, True
                        inputValues[maxControlNetIndex[0]] = ValueType.Unknown

    def getValueIn5(self, net: str, inputValues: list) -> ValueType:
        inputValuesCopy = inputValues.copy()
        for i in range(len(inputValuesCopy)):
            if inputValuesCopy[i] == ValueType.Zero_One:
                inputValuesCopy[i] = ValueType.Zero
            elif inputValuesCopy[i] == ValueType.One_Zero:
                inputValuesCopy[i] = ValueType.One
        correctResult = self.testabilityObj.getValue(net, inputValuesCopy)
        
        inputValuesCopy = inputValues.copy()
        for i in range(len(inputValuesCopy)):
            if inputValuesCopy[i] == ValueType.Zero_One:
                inputValuesCopy[i] = ValueType.One
            elif inputValuesCopy[i] == ValueType.One_Zero:
                inputValuesCopy[i] = ValueType.Zero
        faultyResult = self.testabilityObj.getValue(net, inputValuesCopy)
        
        if correctResult == faultyResult:
            return correctResult
        elif correctResult == ValueType.Zero and faultyResult == ValueType.One:
            return ValueType.Zero_One
        elif correctResult == ValueType.One and faultyResult == ValueType.Zero:
            return ValueType.One_Zero
        else:
            return ValueType.Unknown

    def imply(self, netList: dict, testStack: list, fault: tuple):
        self.clearNetList(netList)
        for tnet in testStack:
            netList[tnet[0]][-1] = tnet[1]
            
        for i in netList.keys():
            net = netList[i]
            if net[2] == 'from':
                for j in netList.keys():
                    if netList[j][1] == net[3]:
                        inputNet = netList[j]
                        net[-1] = inputNet[-1]
                        break
            elif net[2] != "inpt":
                startInputsIndex = len(net) - 1 - int(net[4])
                endInputsIndex = len(net) - 1
                inputNets = [netList[j] for j in net[startInputsIndex: endInputsIndex]]
                inputValues = [inputNet[-1] for inputNet in inputNets]
                net[-1] = self.getValueIn5(net[2], inputValues)
                
            if net[0] == fault[0]:
                if fault[1] == FaultType.SA0 and net[-1] == ValueType.One:
                    net[-1] = ValueType.One_Zero
                elif fault[1] == FaultType.SA1 and net[-1] == ValueType.Zero:
                    net[-1] = ValueType.Zero_One

    def checkDetected(self, netList: dict) -> bool:
        for i in netList.keys():
            net = netList[i]
            if net[2] in ['from', "inpt"]:
                continue
            elif net[3] == "0":
                if net[-1] in [ValueType.One_Zero, ValueType.Zero_One]:
                    return True
        return False

    def generateTestVector(self, testStack: list) -> dict:
        return {tnet[0]: tnet[1] for tnet in testStack}

    def backTrack(self, testStack: list) -> bool:
        if False in [testNt[2] for testNt in testStack]:
            i = -1
            while testStack[i][2]:
                i -= 1
            tNet = testStack[i]
            for j in range(-1, i, -1):
                testStack[j][2] = False
                
            tNet[1] = ValueType.Zero if tNet[1] == ValueType.One else ValueType.One
            tNet[2] = True
            return True
        return False

    def PODEM(self, netList: dict, fault: tuple) -> dict:
        state = "Start"
        objective = None
        testStack = []
        controllabilies = self.testabilityObj.CC_CO
        
        while True:
            if state == "Start":
                self.clearNetList(netList)
                state = "XPathCheck"
            elif state == "XPathCheck":
                if self.xpathCheck(netList, fault):
                    state = "Objective"
                else:
                    state = "BackTrack"
            elif state == "Objective":
                objective = self.obtainObjective(netList, fault, controllabilies)
                if objective is not None:
                    state = "BackTrace"
                else:
                    state = "Finish_Untestable"
            elif state == "BackTrace":
                pi, v = self.backTrace(netList, objective, controllabilies)
                testStack.append([pi, v, False])
                state = "Implication"
            elif state == "Implication":
                self.imply(netList, testStack, fault)
                state = "CheckDetected"
            elif state == "CheckDetected":
                if self.checkDetected(netList):
                    state = "Finish_Success"
                else:
                    state = "XPathCheck"
            elif state == "BackTrack":
                if self.backTrack(testStack):
                    state = "Implication"
                else:
                    state = "Finish_Untestable"
            elif state == "Finish_Success":
                return self.generateTestVector(testStack)
            else:
                return {}

    def globalPODEM(self, netList: dict, faultList: list) -> list:
        return [self.PODEM(netList, fault) for fault in faultList]