class UjcatapiError(Exception):
    pass


class EventException(UjcatapiError):
    pass


class DuplicateEntityError(UjcatapiError):
    pass


class DuplicateCatError(DuplicateEntityError):
    pass


class EmptyResultsFilter(UjcatapiError):
    pass


class EntityNotFoundError(UjcatapiError):
    pass


class CatNotFoundError(EntityNotFoundError):
    pass
