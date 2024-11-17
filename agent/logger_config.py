import logging
from datetime import datetime

def setup_logger():
    """Configure and return the logger instance"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'ai_agent_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('ai_chat')

logger = setup_logger()