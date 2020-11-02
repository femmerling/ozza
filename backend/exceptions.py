class OzzaException(Exception):
    error_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class EmptyParameterException(OzzaException):
    def __init__(self, message="Method parameter should not be empty"):
        self.message = message
        self.status_code = 400
        super().__init__(self)


class IdNotFoundException(OzzaException):
    def __init__(self, message="Value must contain `id` field"):
        self.message = message
        self.status_code = 400
        super().__init__(self)


class MismatchIdException(OzzaException):
    def __init__(self, message="Value `id` mismatched existing `id`"):
        self.message = message
        self.status_code = 400
        super().__init__(self)


class ResourceNotFoundException(OzzaException):
    def __init__(self, message="Resource with that key was not found"):
        self.message = message
        self.status_code = 404
        super().__init__(self)


class FieldNotFoundException(OzzaException):
    def __init__(self, message="Requested field was not found in data"):
        self.message = message
        self.status_code = 500
        super().__init__(self)

class InvalidFilterFormatException(OzzaException):
    def __init__(self, message="Filter item must be dict using `{\"field\":<field name>, \"value\":<field value>}` format"):
        self.message = message
        self.status_code = 400
        super().__init__(self)
