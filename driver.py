from pathlib import Path

def compile_file(
    input_path: str,
    output_path: str,
    debug: bool
):
    if debug:
        print(f"input_path: {input_path},\noutput_path: {output_path}\ndebug: {"true" if debug else "false"}\n")
    pass