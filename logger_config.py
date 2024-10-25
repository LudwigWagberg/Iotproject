import logging

def setup_logger(log_file="loggfile", level=logging.INFO):
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )