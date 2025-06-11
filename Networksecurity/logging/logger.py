import logging
import os
from datetime import datetime

Log_file_format=f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logs_path = os.path.join(os.getcwd(), "logs", Log_file_format)
os.makedirs(log_file_path, exist_ok=True)

# LOgFile PAth
log_file_path = os.path.join(logs_path, Log_file_format)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[ %(asctime)s ]%(lineno)d %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)