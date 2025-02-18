"""Module containing custom exceptions for the Salt River Project Energy API.

Classes:
    InvalidBillingAccountError: Exception raised for invalid billing account.
    InvalidUsernameError: Exception raised for invalid username.
    InvalidPasswordError: Exception raised for invalid password.
"""

class InvalidBillingAccountError(ValueError):
    """Exception raised for invalid billing account."""

    def __init__(self, message="billingAccount must be a 9 digit string."):
        """Initialize the exception with an optional message.

        Args:
            message (str): The error message to be displayed. Defaults to
                "billingAccount must be a 9 digit string.".

        """
        self.message = message
        super().__init__(self.message)

class InvalidUsernameError(ValueError):
    """Exception raised for invalid username."""

    def __init__(self, message="username must be a non-empty string."):
        """Initialize the exception with an optional message.

        Args:
            message (str): The error message to be displayed. Defaults to
                "username must be a non-empty string.".

        """
        self.message = message
        super().__init__(self.message)

class InvalidPasswordError(ValueError):
    """Exception raised for invalid password."""

    def __init__(self, message="password must be a non-empty string."):
        """Initialize the exception with an optional message.

        Args:
            message (str): The error message to be displayed. Defaults to
                "password must be a non-empty string.".

        """
        self.message = message
        super().__init__(self.message)
