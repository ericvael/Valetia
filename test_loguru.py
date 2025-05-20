from valetia.logger import loguru_logger, get_logger

# Logger structlog
structured_logger = get_logger(__name__)
structured_logger.info("Message via structlog")
structured_logger.info("Message structuré", user="test_user", action="login")

# Logger loguru
loguru_logger.info("Message via loguru")
loguru_logger.debug("Debug message loguru")
loguru_logger.warning("Warning message")
loguru_logger.error("Error message")

# Test avec contexte
with loguru_logger.contextualize(user_id=123, session_id="abc456"):
    loguru_logger.info("Action dans un contexte spécifique")
