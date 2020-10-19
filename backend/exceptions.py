
class OzzaException(Exception):
    error_code = 500
    payload = None

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        if payload:
            self.payload = payload

class EmptyParameterException(OzzaException):
    def __init__(self, message="Method parameter should not be empty", status_code=400)

class DirectoryCreationException(OzzaException):
    def __init__(self, message="Can't create directory"):
        OzzaException.__init__(message=message)

class IdNotFoundException(OzzaException):
    def __init__(self, message="Value must contain `id` field"):
        OzzaException.__init__(message=message, status_code=400)

class ResourceGroupNotFoundException(OzzaException):
    def __init__(self, message="Resource with that key was not found"):
        OzzaException.__init__(message=message, status_code=404)

class FieldNotFoundException(OzzaException):
    def __init__(self, message="Requested field was not found in data"):
        OzzaException.__init__(message=message, status_code=400)

class DataWriteException(IOError, OzzaException):
    def __init__(self, message="Data write error"):
        IOError.__init__(self)
        OzzaException.__init__(message=message, status_code=500)

class DirectoryOperationException(OSError, OzzaException):
    def __init__(self, messaage="Directory operation error"):
        OSError.__init__(self)
        OzzaException.__init__(message=message, status_code=500)
