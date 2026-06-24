#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import subprocess
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_step(label, command):
    print("== %s ==" % label)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run compact GPGPU skill CI gates.")
    parser.add_argument("--mode", default="asset", choices=["asset", "local-tools"])
    parser.add_argument("--config", help="Local toolchain config for local-tools mode.")
    parser.add_argument(
        "--example",
        default=os.path.join(ROOT, "shared", "examples", "minimal_simt"),
        help="Example directory for e2e vertical slice.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    py = sys.executable
    run_step("asset validation", [py, os.path.join(ROOT, "shared", "tests", "validate_compact_assets.py")])
    print("ASSET_VALIDATION_PASS")
    run_step("schema validation", [py, os.path.join(ROOT, "tools", "validate_ir_schemas.py")])
    run_step("case gate", [py, os.path.join(ROOT, "tools", "validate_cases.py")])
    run_step("contract path validation", [py, os.path.join(ROOT, "tools", "validate_contract_paths.py")])
    run_step(
        "canonical hash validation",
        [py, os.path.join(ROOT, "tools", "validate_canonical_hashes.py"), "--mode", "legacy-compatible"],
    )
    run_step(
        "e2e vertical slice asset mode",
        [py, os.path.join(ROOT, "tools", "e2e_vertical_slice_runner.py"), "--mode", "asset", "--example", args.example],
    )

    if args.mode == "local-tools":
        command = [
            py,
            os.path.join(ROOT, "tools", "e2e_vertical_slice_runner.py"),
            "--mode",
            "local-tools",
            "--example",
            args.example,
        ]
        if args.config:
            command.extend(["--config", args.config])
        run_step("e2e vertical slice local tools", command)


if __name__ == "__main__":
    main()
