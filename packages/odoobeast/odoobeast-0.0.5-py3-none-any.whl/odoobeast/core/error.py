import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('odoobeast.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('OdooBeast')

class OdooBeastError(Exception):
    """Custom exception class for OdooBeast"""
    pass

# Error handling function
def handle_error(error_message):
    logger.error(error_message)
    raise OdooBeastError(error_message)

# Example usage
if __name__ == "__main__":
    try:
        raise ValueError("This is a test error")
    except ValueError as e:
        handle_error(f"An error occurred: {str(e)}")
