class CliCommonException(Exception):
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            original_message = f" (caused by {self.original_exception})"
        else:
            original_message = ""
        return f"{super().__str__()}{original_message}"
