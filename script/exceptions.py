class ConflictingCommandHandlerError(Exception):
    pass


class UserParameterValidationError(Exception):
    def __init__(self, message):
        super().__init__(self.__class__.__name__ + ": " + message)


class UserMappingValidationError(Exception):
    def __init__(self, message):
        super().__init__(self.__class__.__name__ + ": " + message)
