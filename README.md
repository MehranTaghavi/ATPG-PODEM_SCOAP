# ATPG, PODEM, and SCOAP Testability Analysis

<div align="center">
  <img src="https://img.shields.io/badge/Language-Python%203.x-blue.svg" alt="Python 3.x">
  <img src="https://img.shields.io/badge/Domain-Digital%20Testability-orange.svg" alt="Digital testability">
  <img src="https://img.shields.io/badge/Algorithms-PODEM%20%7C%20SCOAP-800000.svg" alt="PODEM and SCOAP">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License MIT">
</div>

<p align="center">
  <img src="docs/images/PODEM.png" alt="Hardware test analysis project with Python" width="100%">
</p>

This repository contains a modular Python implementation of testability analysis for combinational digital circuits. It combines two coursework phases in one project:

- **Phase one:** four-valued logic simulation and timing-aware propagation.
- **Phase two:** SCOAP controllability/observability analysis and PODEM automatic test-pattern generation.

The project supports ISCAS-style netlists, single stuck-at faults, and benchmark circuits such as `c1`, `c5`, `c17`, `c432`, `c6288`, and `c7552`.

## Project Workflow

The single entry point runs all analyses for the selected circuit through a Command Line Interface (CLI):

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