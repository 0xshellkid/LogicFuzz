#!/usr/bin/env python3


import argparse
import os
import sys

from LogicFuzz.ProgramGeneration import generator
from LogicFuzz.ProgramMutation import mutator
from LogicFuzz.InputDelivery import deliverer
from LogicFuzz.Monitor import monitor

SUPPORTED_MODELS = ["gpt-3.5", "gpt-4", "Deepseek-R1", "Deepseek-V3"]


def parse_args():
    parser = argparse.ArgumentParser(description="LogicFuzz CLI")
    parser.add_argument(
        "--mode",
        choices=["generate", "mutate", "deliver", "monitor"],
        required=True,
        help="Operation mode: generate | mutate | deliver | monitor",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        help="Name of the logic instruction to process",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gpt-4",
        help="LLM model for test-program generation",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./results",
        help="Directory to save generated programs or mutation outputs",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="IP address of the PLC for input delivery",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)

    if args.mode == "generate":
        if not args.instruction:
            sys.exit("ERROR: --instruction is required for generate mode")
        generator.generate_test_program(
            instruction=args.instruction,
            model=args.model,
            output_dir=args.output,
        )

    elif args.mode == "mutate":
        if not args.instruction:
            sys.exit("ERROR: --instruction is required for mutate mode")
        mutator.mutate_instruction(
            instruction=args.instruction,
            output_dir=args.output,
        )

    elif args.mode == "deliver":
        if not args.target or not args.instruction:
            sys.exit("ERROR: --target and --instruction are required for deliver mode")
        deliverer.deliver_to_plc(
            plc_ip=args.target,
            instruction=args.instruction,
            input_dir=args.output,
        )

    elif args.mode == "monitor":
        monitor.start_monitor()

    else:
        sys.exit(f"ERROR: Unknown mode '{args.mode}'")


if __name__ == "__main__":
    main()
