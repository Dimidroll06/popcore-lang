import argparse
from driver import compile_file
from helpers.logger import *

def main():
    parser = argparse.ArgumentParser(
        prog="popcore",
        description="PopCore compiler — low-level, safe, educational"
    )
    parser.add_argument(
        "input",
        help="Input file (.prcore)"
    )
    parser.add_argument(
        "-o", 
        "--output", 
        help="Output assembly file (.s)"
    )
    parser.add_argument(
        "-g", 
        "--debug", 
        action="store_true",
        help="Print debug info (AST)"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="popcore 0.1"
    )

    args = parser.parse_args()
    logger = Logger(args.debug)
    
    if (not args.input.endswith('.pcore')):
        logger.error('Compiler works only with .pcore files')
        exit(1)
        
    output = args.output or args.input.replace('.pcore', '.s')
    
    compile_file(
        input_path=args.input,
        output_path=output,
        debug=args.debug
    )