from pathlib import Path
from helpers.logger import Logger
from compilers.preprocessor import process_file

def compile_file(
    input_path: str,
    output_path: str,
    debug: bool
):
    logger = Logger(debug)
    
    input_full_path = Path(input_path)
    output_full_path = Path(output_path)
    
    logger.debug(
        f"input: {input_full_path}\n",
        f"output: {input_full_path}\n"
    )

    stopOnPreprocess = output_path.endswith(".ppcore")
    
    logger.debug("Starting preprocessing file")
    preprocessed = process_file(input_full_path, {})
    logger.debug(f"Preprocessed, got {len(preprocessed)} characters")

    if stopOnPreprocess:
        logger.info("Saved to file succesfully")
        output_full_path.write_text(preprocessed, 'utf-8')
        return
    
    pass