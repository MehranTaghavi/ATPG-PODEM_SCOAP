"""
constants.py
Defines the standard Enums and constant values used across the ATPG project.
"""
from enum import Enum

class FaultType(Enum):
    SA0 = "sa-0"
    SA1 = "sa-1"

class ValueType(Enum):
    One = "1"
    Zero = "0"
    Unknown = "U"
    HighZ = "Z"
    One_Zero = "D"   
    Zero_One = "~D"