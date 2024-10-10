import logging


class AccQsureException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def __repr__(self):
        return "AccQsureException( {self.message!r})".format(self=self)

    def __str__(self):
        return "AccQsureException({self.message!r})".format(self=self)


class ApiError(AccQsureException):
    def __init__(self, status, data, *args):
        super().__init__(data, *args)
        self._status = status
        logging.debug(data)
        self._message = data.get("errorMessage") or data.get("message")

    @property
    def status(self) -> int:
        return self._status

    def __repr__(self):
        return "ApiError({self.status}, {self.message!r})".format(self=self)

    def __str__(self):
        return "ApiError({self.status}, {self.message!r})".format(self=self)


class SpecificationError(AccQsureException):
    def __init__(self, attribute, message, *args):
        super().__init__(message, *args)
        self._attribute = attribute
        self._message = message

    @property
    def attribute(self) -> str:
        return self._attribute

    def __repr__(self):
        return "SpecificationError({self.attribute}, {self.message})".format(self=self)

    def __str__(self):
        return "SpecificationError({self.attribute}, {self.message})".format(self=self)
