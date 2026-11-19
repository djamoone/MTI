
from abc import ABC, abstractmethod


# Abstract Interface
class ILogger(ABC):

    @abstractmethod
    def log(self, message):
        pass


# Concrete Implementation 1
class FileLogger(ILogger):

    def log(self, message):
        print(f"Logging to file: {message}")


# Concrete Implementation 2
class DatabaseLogger(ILogger):

    def log(self, message):
        print(f"Logging to database: {message}")


# High-Level Module
class Application:

    def __init__(self, logger: ILogger):
        self.logger = logger

    def start(self):
        self.logger.log("Application started")


# Main
if __name__ == "__main__":

    # Using FileLogger
    file_logger = FileLogger()
    app = Application(file_logger)
    app.start()

    # Using DatabaseLogger
    database_logger = DatabaseLogger()
    app = Application(database_logger)
    app.start()
