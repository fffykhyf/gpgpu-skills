#!/usr/bin/env python3
import os
import sys

sys.dont_write_bytecode = True

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

from validate_cases import main as validate_cases
from validate_canonical_hashes import main as validate_canonical_hashes
from validate_compact_assets import main as validate_assets
from validate_contract_paths import main as validate_contract_paths
from validate_ir_schemas import main as validate_ir_schemas

if __name__ == "__main__":
    validate_assets()
    validate_ir_schemas([])
    validate_cases([])
    validate_contract_paths([])
    validate_canonical_hashes(["--mode", "legacy-compatible"])
