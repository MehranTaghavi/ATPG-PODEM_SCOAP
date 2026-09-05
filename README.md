# Automated Test Pattern Generation with PODEM and SCOAP

<div align="center">
  <img src="https://img.shields.io/badge/Language-Python%203.x-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Domain-Electronic%20Design%20Automation-orange.svg" alt="Electronic Design Automation">
  <img src="https://img.shields.io/badge/Method-PODEM%20%7C%20SCOAP-800000.svg" alt="PODEM and SCOAP">
  <img src="https://img.shields.io/badge/Institution-Sharif%20University%20of%20Technology-800000.svg" alt="Sharif University of Technology">
</div>

An educational, modular Python implementation of **Automatic Test Pattern Generation (ATPG)** for combinational digital circuits. The project combines **SCOAP** testability metrics with the **PODEM** algorithm to generate input test vectors for single stuck-at faults.

The implementation supports the standard five-valued fault simulation symbols and parses ISCAS benchmark netlists such as `c5`, `c17`, `c432`, `c6288`, and `c7552`.

> **Academic project:** Developed by **Mehran Taghavi** for coursework in Testability and Hardware Testing at **Sharif University of Technology**.

## Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Supported Logic](#supported-logic)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Input and Output Formats](#input-and-output-formats)
- [Repository Structure](#repository-structure)
- [Implementation Notes and Limitations](#implementation-notes-and-limitations)
- [Technical Report](#technical-report)
- [License](#license)

## Features

- **PODEM ATPG:** Objective selection, SCOAP-guided backtrace, implication, XPath checking, fault detection, and backtracking.
- **Five-valued fault logic:** `0`, `1`, `U` (unknown), `D` (good `1`, faulty `0`), and `~D` (good `0`, faulty `1`).
- **SCOAP analysis:** Computes combinational controllability (`CC0`, `CC1`) and observability (`CO`) for the parsed circuit nodes.
- **Logic gates:** `AND`, `OR`, `NAND`, `NOR`, `XOR`, `XNOR`, `NOT`, `BUFF`, and `BUF`.
- **ISCAS-style input:** Reads `.isc` netlists and matching fault-list files.
- **Generated artifacts:** Writes one test-vector table and one SCOAP matrix for each analyzed circuit.
- **Small, separable architecture:** Parsing, gate evaluation, SCOAP computation, PODEM search, and execution flow are kept in separate modules.

## How It Works

For each fault, the PODEM driver follows the conventional ATPG loop:

1. **Initialize** the circuit state and clear all node assignments.
2. **XPath check** to determine whether the fault effect can still reach a primary output.
3. **Objective selection** to excite the fault or propagate an existing D-value through the D-frontier.
4. **Backtrace** from the objective to a primary input, using controllability values to choose assignments.
5. **Imply** the selected input assignment through the circuit using five-valued logic.
6. **Check detection** at a primary output.
7. **Backtrack** and try the complementary input value when the current branch cannot produce a test.

The implementation uses `CC0` and `CC1` as heuristics during objective selection and backtrace. `CO` is calculated and exported as part of the SCOAP report.

### SCOAP example

For a two-input `AND` gate, the standard combinational controllability equations are:

$$
CC0(Y) = \min(CC0(X_1), CC0(X_2)) + 1
$$

$$
CC1(Y) = CC1(X_1) + CC1(X_2) + 1
$$

Lower controllability values represent easier assignments. The complete theoretical background, flowcharts, and manual traces are available in the [technical report](docs/Testability_Technical_Report.pdf.pdf).

## Supported Logic

| Symbol | Meaning                                 |
| ------ | --------------------------------------- |
| `0`  | Logic zero                              |
| `1`  | Logic one                               |
| `U`  | Unknown or unassigned value             |
| `D`  | Good circuit`1`, faulty circuit `0` |
| `~D` | Good circuit`0`, faulty circuit `1` |

The fault model is the single stuck-at model:

- `sa0`: the selected node is permanently stuck at `0`;
- `sa1`: the selected node is permanently stuck at `1`.

## Requirements

- Python 3.x
- No third-party Python packages are required.
- Run commands from the repository root so that the `src` package can be imported correctly.

## Quick Start

Clone the repository and run the default `c5` analysis:

```bash
git clone <repository-url>
cd ATPG-PODEM_SCOAP
python -m src.main
```

The program reads:

```text
data/inputs/c5.isc
data/inputs/c5_fault.txt
```

and writes:

```text
data/outputs/c5_test_vectors.txt
data/outputs/c5_SCOAP.txt
```

To analyze another circuit, change the `circuit` value near the bottom of [src/main.py](src/main.py):

```python
circuit = "c17"
```

The corresponding files must exist in `data/inputs/` using the naming convention `<circuit>.isc` and `<circuit>_fault.txt`.

## Input and Output Formats

### Netlist and fault list

Each circuit is represented by an ISCAS-style `.isc` netlist. Its fault list contains one fault per line:

```text
1 sa0
1 sa1
2 sa0
2 sa1
```

The node name and fault type must match the parser's expected format. Fanout branch faults are resolved from the corresponding ISCAS branch notation.

### Test-vector output

The generated `<circuit>_test_vectors.txt` file contains the fault, followed by values for each primary input. A `U` means that the input is unspecified and may be assigned either binary value. `none found` indicates that the current search did not generate a test vector for that fault.

Example:

```text
net     fault   1   2   4
-------------------------
1       sa-0    1   1   1
1       sa-1    0   1   1
```

### SCOAP output

The generated `<circuit>_SCOAP.txt` file contains one row per parsed node:

```text
net     CC0   CC1   CO
--------------------------
1       1     1     4
2       1     1     4
5       2     4     0
```

## Repository Structure

```text
ATPG-PODEM_SCOAP/
├── data/
│   ├── inputs/                         # ISCAS netlists and fault lists
│   └── outputs/                        # Generated test vectors and SCOAP tables
├── docs/
│   └── Testability_Technical_Repor.pdf
├── src/
│   ├── constants.py                    # Logic and fault-type enumerations
│   ├── gates.py                        # Gate evaluation and SCOAP formulas
│   ├── scoap.py                        # Netlist parsing and CC/CO calculation
│   ├── podem.py                        # PODEM search and five-valued implication
│   └── main.py                         # Application entry point and file export
└── README.md
```

## Implementation Notes and Limitations

- The current entry point selects the circuit through a variable in `src/main.py`; a command-line interface is not included yet.
- The implementation targets combinational ISCAS-style circuits and single stuck-at faults.
- Generated vectors are reported for the primary inputs; unspecified inputs are written as `U`.
- No automated test suite or fault-coverage summary is currently included in the repository.
- The current sample output contains results for `c5`; the other benchmark inputs are provided for analysis.

These points describe the current project scope and are useful when comparing results with a production ATPG tool.

## Technical Report

The detailed derivations, algorithm flowcharts, and worked examples are available in the [Testability Technical Report](docs/Testability_Technical_Report.pdf.pdf).

## License

No open-source license has been declared yet. Until a license is added, the repository should be treated as **all rights reserved**.
