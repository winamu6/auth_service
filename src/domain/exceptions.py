from typing import Any


class DomainException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

class EntityNotFoundException(DomainException):
    def __init__(self, entity_name: str, entity_id: int):
        message = f"{entity_name} с ID {entity_id} не найден(а)."
        super().__init__(message, status_code=404)
        self.entity_name = entity_name
        self.entity_id = entity_id

class EntityAlreadyExistsException(DomainException):
    def __init__(self, entity_name: str, field: str, value: Any):
        message = f"{entity_name} с полем {field}='{value}' уже существует."
        super().__init__(message, status_code=409)

class RepositoryOperationError(DomainException):
    def __init__(self, detail: str = "Не удалось выполнить операцию с базой данных."):
        super().__init__(detail, status_code=500)

class PermissionDeniedException(DomainException):
    def __init__(self, detail: str = "Недостаточно прав для выполнения операции."):
        super().__init__(detail, status_code=403)

class ObjectIsDeletedException(DomainException):
    def __init__(self, entity_name: str, entity_id: int):
        message = f"{entity_name} с ID {entity_id} был(а) удален(а)."
        super().__init__(message, status_code=410)

class TeamCapacityExceededException(DomainException):
    def __init__(self, max_staffs: int = 4):
        message = f"Превышена максимальная вместимость команды: допускается до {max_staffs} сотрудников."
        super().__init__(message, status_code=400)

class InvalidWorkDatesException(DomainException):
    def __init__(self):
        message = "Дата начала плановых работ не может быть позже даты окончания."
        super().__init__(message, status_code=400)