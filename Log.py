from datetime import datetime
import logging
import os

# Log class to handle log messages
class Log:

    # Setup log configration 
    @classmethod
    def log_config(self, in_terminal: bool = False):
        log_location = os.getenv("LOGS_LOCATION")
        file_name = "log-" + datetime.now().strftime("%Y-%m-%d") + ".log"
        if(log_location[-1] != "/"):
            log_location = log_location + '/'
        file_path = log_location + file_name
        if(in_terminal):
            file_path = ''
        logging.basicConfig(filename = file_path,
                    format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    # Show log in terminal
    @classmethod
    def show_log_in_terminal(self, type, message):
        self.log_config(True)
        self.message(type, message)
        
    # Show log in file
    @classmethod
    def write_log_in_file(self, type, message):
        self.log_config(False)
        self.message(type, message)
    
    @classmethod
    def message(self, type, message):
        if(type == 'warning'):
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)
            logger.debug(message)
            logger.warning(message)
            del logger
        elif(type == 'info'):
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            logger.debug(message)
            logger.info(message)
            del logger
        elif(type == 'debug'):
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            logger.debug(message)
            del logger
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.ERROR)
            logger.debug(message)
            logger.error(message)
            del logger
            exit()