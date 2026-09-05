# ATPG, PODEM, and SCOAP Testability Analysis

<div align="center">
  <img src="https://img.shields.io/badge/Language-Python%203.x-blue.svg" alt="Python 3.x">
  <img src="https://img.shields.io/badge/Domain-Digital%20Testability-orange.svg" alt="Digital testability">
  <img src="https://img.shields.io/badge/Algorithms-PODEM%20%7C%20SCOAP-800000.svg" alt="PODEM and SCOAP">
</div>

This repository contains a modular Python implementation of testability analysis for combinational digital circuits. It combines two coursework phases in one project:

- **Phase one:** four-valued logic simulation and timing-aware propagation.
- **Phase two:** SCOAP controllability/observability analysis and PODEM automatic test-pattern generation.

The project supports ISCAS-style netlists, single stuck-at faults, and benchmark circuits such as `c1`, `c5`, `c17`, `c432`, `c6288`, and `c7552`.

## Project Workflow

The single entry point runs all analyses for the selected circuit:

```text
ISCAS netlist + input values + fault list
                    |
                    v
        Phase 1: true values and delay
                    |
                    v
        Phase 2: SCOAP and PODEM ATPG
                    |
                    v
                 output/
```

The default circuit is `c5`. Running the program creates exactly four result files:

```text
output/c5_true_values.txt
output/c5_delay.txt
output/c5_test_vectors.txt
output/c5_SCOAP.txt
```

## Quick Start

Requirements:

- Python 3.x
- No third-party packages
- Commands executed from the repository root

```powershell
git clone https://github.com/MehranTaghavi/ATPG-PODEM_SCOAP.git
cd ATPG-PODEM_SCOAP
python -m src.main
```

To analyze another circuit, change the `circuit` value at the bottom of [src/main.py](src/main.py):

```python
circuit = "c17"
```

The selected circuit must have the required `.isc`, input-vector, and fault-list files in `data/inputs/`. Delay-aware netlists and vectors are stored in `data/inputs/delay/`.

## Source Modules

| Module | Responsibility |
| --- | --- |
| [src/main.py](src/main.py) | Single application entry point; runs both phases and creates `output/`. |
| [src/four_valued_logic.py](src/four_valued_logic.py) | Defines `0`, `1`, `U`, and `Z`, plus phase-one gate operations. |
| [src/true_value.py](src/true_value.py) | Parses an ISCAS netlist and propagates combinational true values over input time steps. |
| [src/delay.py](src/delay.py) | Propagates values through delay-annotated netlists and calculates timing-aware outputs. |
| [src/constants.py](src/constants.py) | Defines the five-valued PODEM logic and stuck-at fault types. |
| [src/gates.py](src/gates.py) | Implements gate evaluation and SCOAP controllability formulas. |
| [src/scoap.py](src/scoap.py) | Parses ISCAS/fault files and calculates `CC0`, `CC1`, and `CO`. |
| [src/podem.py](src/podem.py) | Implements objective selection, backtrace, implication, XPath checking, and backtracking. |

## Phase One

### True-value analysis

`true_value.py` evaluates each node for every input time step using the four-valued set:

| Value | Meaning |
| --- | --- |
| `0` | Logic zero |
| `1` | Logic one |
| `U` | Unknown or unassigned |
| `Z` | High impedance |

The result is written to `<circuit>_true_values.txt`.

### Delay analysis

`delay.py` evaluates delay-annotated ISCAS netlists. It propagates each gate's value at the appropriate time and accounts for the maximum path delay. The result is written to `<circuit>_delay.txt`.

## Phase Two: SCOAP and PODEM

PODEM generates test vectors for single stuck-at faults using this loop:

1. Initialize the circuit state.
2. Check whether an activation path can reach a primary output.
3. Select an objective to excite or propagate the fault.
4. Backtrace the objective to a primary input using controllability values.
5. Imply the assignment through the circuit using five-valued logic.
6. Check whether the fault is observable at a primary output.
7. Backtrack and try the complementary assignment when necessary.

SCOAP calculates:

- `CC0`: difficulty of controlling a node to `0`;
- `CC1`: difficulty of controlling a node to `1`;
- `CO`: difficulty of observing a node at a primary output.

For a two-input `AND` gate:

$$
CC0(Y) = \min(CC0(X_1), CC0(X_2)) + 1
$$

$$
CC1(Y) = CC1(X_1) + CC1(X_2) + 1
$$

The test-vector table is written to `<circuit>_test_vectors.txt`, and the SCOAP table is written to `<circuit>_SCOAP.txt`.

## Input Files

Standard ATPG inputs are stored in `data/inputs/`:

```text
data/inputs/c5.isc
data/inputs/c5_inputs_values.txt
data/inputs/c5_fault.txt
```

Fault lists use one fault per line:

```text
1 sa0
1 sa1
2 sa0
2 sa1
```

## Repository Structure

```text
ATPG-PODEM_SCOAP/
├── data/
│   └── inputs/
│       ├── *.isc                         # Standard ISCAS netlists
│       ├── *_fault.txt                   # Single stuck-at fault lists
│       ├── *_inputs_values.txt           # Phase-one input values
│       └── delay/                         # Delay-annotated phase-one inputs
├── docs/
│   ├── Phase1_Testability_Analysis_Report.pdf
│   └── Testability_Technical_Report.pdf.pdf
├── output/                                # Generated results from src.main
├── src/
│   ├── constants.py
│   ├── four_valued_logic.py
│   ├── true_value.py
│   ├── delay.py
│   ├── gates.py
│   ├── scoap.py
│   ├── podem.py
│   └── main.py
├── .gitignore
└── README.md
```

## Reports

- [Phase One Testability Analysis Report](docs/Phase1_Testability_Analysis_Report.pdf)
- [PODEM and SCOAP Technical Report](docs/Testability_Technical_Report.pdf.pdf)

## Scope and Limitations

- The implementation targets combinational ISCAS-style circuits.
- The fault model is single stuck-at `sa0` and `sa1`.
- The current entry point selects the circuit by editing one variable in `src/main.py`.
- No automated fault-coverage summary is generated yet.
- No open-source license has been declared for this academic repository.

## Author

Developed by **Mehran Taghavi** as part of Testability and Hardware Testing coursework at **Sharif University of Technology**.
