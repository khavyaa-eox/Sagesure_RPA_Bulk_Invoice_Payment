import logging

#--------------------- Logger for listener.py ---------------------#
# Set up logging for listener.py
listener_logger = logging.getLogger('listener_logger')
listener_logger.setLevel(logging.INFO)

# Create a file handler for app.log
listener_file_handler = logging.FileHandler('app.log')
listener_file_handler.setLevel(logging.INFO)

# Create a logging format for listener logger
listener_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
listener_file_handler.setFormatter(listener_formatter)

# Add the handler to the listener_logger
listener_logger.addHandler(listener_file_handler)

# Disable propagation to the root logger
listener_logger.propagate = False

#--------------------- Logger for Bulk_Invoice_Payment.py ---------------------#
# Set up logging for Bulk_Invoice_Payment.py
bulk_invoice_logger = logging.getLogger('bulk_invoice_logger')
bulk_invoice_logger.setLevel(logging.INFO)

# Create a file handler for record.log
bulk_invoice_file_handler = logging.FileHandler('record.log')
bulk_invoice_file_handler.setLevel(logging.INFO)

# Create a logging format for bulk_invoice logger
bulk_invoice_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bulk_invoice_file_handler.setFormatter(bulk_invoice_formatter)

# Add the handler to the bulk_invoice_logger
bulk_invoice_logger.addHandler(bulk_invoice_file_handler)

# Disable propagation to the root logger
bulk_invoice_logger.propagate = False

def log_separator(logger, char='-', length=80):
    logger.info(char * length)