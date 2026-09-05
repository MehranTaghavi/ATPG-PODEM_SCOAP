"""
main.py
Main entry point for generating Test Vectors and SCOAP analysis matrices.
"""
import os
from src.constants import FaultType
from src.scoap import Testability
from src.gates import register_all_gates
from src.podem import PODEM
from src.delay import export_delay_values
from src.true_value import export_true_values

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

def run_phase_one(circuit_name: str, input_dir: str, output_dir: str) -> None:
    input_path = os.path.join(input_dir, f"{circuit_name}_inputs_values.txt")
    isc_path = os.path.join(input_dir, f"{circuit_name}.isc")
    export_true_values(
        input_path,
        isc_path,
        os.path.join(output_dir, f"{circuit_name}_true_values.txt"),
    )
    export_delay_values(
        os.path.join(input_dir, "delay", f"{circuit_name}_inputs_values.txt"),
        os.path.join(input_dir, "delay", f"{circuit_name}.isc"),
        os.path.join(output_dir, f"{circuit_name}_delay.txt"),
    )


def run_phase_two(circuit_name: str, input_dir: str, output_dir: str) -> None:
    exportTestVectors(
        os.path.join(input_dir, f"{circuit_name}.isc"),
        os.path.join(input_dir, f"{circuit_name}_fault.txt"),
        os.path.join(output_dir, f"{circuit_name}_test_vectors.txt"),
        os.path.join(output_dir, f"{circuit_name}_SCOAP.txt"),
    )


def run_all(circuit_name: str = "c5") -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "data", "inputs")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    run_phase_one(circuit_name, input_dir, output_dir)
    run_phase_two(circuit_name, input_dir, output_dir)

if __name__ == "__main__":
    circuit = "c5"  # می توانید این نام را به c17 یا c432 تغییر دهید
    print(f"Running ATPG Analysis for {circuit}...")
    run_all(circuit)
    print("Execution completed successfully. Check 'output/'")