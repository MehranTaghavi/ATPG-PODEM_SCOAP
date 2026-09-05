"""
main.py
Main entry point for generating Test Vectors and SCOAP analysis matrices.
"""
import os
from src.constants import FaultType
from src.scoap import Testability
from src.gates import register_all_gates
from src.podem import PODEM

def exportTestVectors(inputFilePath: str, faultFilePath: str, testVectorsPath: str, SCOAPpath: str):
    testability_obj = Testability()
    register_all_gates(testability_obj)
    podem_obj = PODEM(testability_obj)

    with open(inputFilePath, 'r') as inputFile, open(faultFilePath, 'r') as faultFile:
        faultListToprint = []
        for line in faultFile.readlines():
            splittedLine = line.strip().split()
            splittedLine[1] = FaultType.SA0 if splittedLine[1] == "sa0" else FaultType.SA1
            faultListToprint.append(splittedLine)
            
        netList = testability_obj.readISC(inputFile)
        faultList = testability_obj.readFaults(faultFile, netList)
        
        testability_obj.CC_CO = {}
        testability_obj.calculateControllability(netList)
        testability_obj.calculateObservability(netList)
        
        testVectors = podem_obj.globalPODEM(netList, faultList)
        
        inputs = [net[0] for net in netList.values() if net[2] == "inpt"]
        
        with open(testVectorsPath, "w") as testF:
            testF.write(f"{'net':<8}{'fault':<8}")
            for input_net in inputs:
                testF.write(f"{input_net:<4}")
            testF.write("\n-------------" + len(inputs) * "----")
            
            for f, testVector in enumerate(testVectors):
                testF.write("\n")
                testF.write(f"{faultListToprint[f][0]:<8}{faultListToprint[f][1].value:<8}")
                if len(testVector.keys()) == 0:
                    testF.write("none found")
                else:
                    for input_net in inputs:
                        if input_net in testVector:
                            testF.write(f"{testVector[input_net].value:<4}")
                        else:
                            testF.write(f"{'U':<4}")
                            
        with open(SCOAPpath, "w") as SCOAPF:
            SCOAPF.write(f"{'net':<8}{'CC0':<6}{'CC1':<6}{'CO':<6}\n")
            SCOAPF.write("-" * 26 + "\n")
            for net in testability_obj.CC_CO:
                SCOAPF.write(f"{net:<8}")
                SCOAPF.write(f"{testability_obj.CC_CO[net]['CC'][0]:<6}")
                SCOAPF.write(f"{testability_obj.CC_CO[net]['CC'][1]:<6}")
                SCOAPF.write(f"{testability_obj.CC_CO[net]['CO']:<6}\n")

def runExportVectors(circuitName: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    input_path = os.path.join(base_dir, "data", "inputs", f"{circuitName}.isc")
    fault_path = os.path.join(base_dir, "data", "inputs", f"{circuitName}_fault.txt")
    vector_out_path = os.path.join(base_dir, "data", "outputs", f"{circuitName}_test_vectors.txt")
    scoap_out_path = os.path.join(base_dir, "data", "outputs", f"{circuitName}_SCOAP.txt")
    
    
    os.makedirs(os.path.dirname(vector_out_path), exist_ok=True)
    exportTestVectors(input_path, fault_path, vector_out_path, scoap_out_path)

if __name__ == "__main__":
    circuit = "c5"  # می توانید این نام را به c17 یا c432 تغییر دهید
    print(f"Running ATPG Analysis for {circuit}...")
    runExportVectors(circuit)
    print("Execution completed successfully. Check 'data/outputs/'")