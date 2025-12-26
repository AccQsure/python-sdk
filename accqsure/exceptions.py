import logging
from typing import Any


class AccQsureException(Exception):
    """Base exception class for all AccQsure SDK errors.

    This is the parent class for all exceptions raised by the SDK.
    All SDK-specific exceptions inherit from this class.
    """

    def __init__(self, message: str, *args: Any) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing the exception.
            *args: Additional positional arguments passed to parent Exception.
        """
        super().__init__(message, *args)
        self._message = message

    @property
    def message(self) -> str:
        """Get the error message.

        Returns:
            The error message string.
        """
        return self._message

    def __repr__(self) -> str:
        return "AccQsureException( {self.message!r})".format(self=self)

    def __str__(self) -> str:
        return "AccQsureException({self.message!r})".format(self=self)


class ApiError(AccQsureException):
    """Exception raised when the API returns an error response.

    This exception is raised when an HTTP request to the AccQsure API
    returns a 4xx or 5xx status code. The status code and error details
    from the API response are included in the exception.
    """

    def __init__(self, status: int, data: dict[str, Any], *args: Any) -> None:
        """Initialize the API error.

        Args:
            status: HTTP status code from the API response.
            data: Error data dictionary from the API response.
            *args: Additional positional arguments passed to parent Exception.
        """
        super().__init__(data, *args)
        self._status = status
        logging.debug(data)
        self._message = data.get("errorMessage") or data.get("message")

    @property
    def status(self) -> int:
        """Get the HTTP status code.

        Returns:
            The HTTP status code from the API response.
        """
        return self._status

    def __repr__(self) -> str:
        return "ApiError({self.status}, {self.message!r})".format(self=self)

    def __str__(self) -> str:
        return "ApiError({self.status}, {self.message!r})".format(self=self)


class SpecificationError(AccQsureException):
    """Exception raised when a required field or parameter is missing or invalid.

    This exception is raised when a method is called with invalid parameters
    or when a required field is missing from a data structure.
    """

    def __init__(self, attribute: str, message: str, *args: Any) -> None:
        """Initialize the specification error.

        Args:
            attribute: Name of the attribute or parameter that caused the error.
            message: Error message describing what went wrong.
            *args: Additional positional arguments passed to parent Exception.
        """
        super().__init__(message, *args)
        self._attribute = attribute
        self._message = message

    @property
    def attribute(self) -> str:
        """Get the attribute name that caused the error.

        Returns:
            The name of the attribute or parameter that caused the error.
        """
        return self._attribute

    def __repr__(self) -> str:
        return "SpecificationError({self.attribute}, {self.message})".format(
            self=self
        )

    def __str__(self) -> str:
        return "SpecificationError({self.attribute}, {self.message})".format(
            self=self
        )


class TaskError(AccQsureException):
    """Exception raised when a background task fails or is canceled.

    This exception is raised when polling a task status shows that the task
    has failed or been canceled. The task result (error details) is included
    in the exception message.
    """

    def __init__(self, message: Any, *args: Any) -> None:
        """Initialize the task error.

        Args:
            message: Error message or result data from the failed task.
            *args: Additional positional arguments passed to parent Exception.
        """
        super().__init__(message, *args)
        self._message = message

    def __repr__(self) -> str:
        return "TaskError({self.message})".format(self=self)

    def __str__(self) -> str:
        return "TaskError({self.message})".format(self=self)
