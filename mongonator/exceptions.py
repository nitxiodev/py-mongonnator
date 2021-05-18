class BaseError(Exception):
    pass


class MongonatorError(BaseError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        expression -- input expression in which the error occurred
    """

    def __init__(self, message, expression=None):
        self.expression = expression
        self.message = message

    def __str__(self):
        return str(self.message)
