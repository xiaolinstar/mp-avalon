from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class BaseGameException(Exception):
    message: str
    error_code: str
    details: Optional[Dict] = None
    cause: Optional[Exception] = None

    def __str__(self):
        return f"[{self.error_code}] {self.message}"

class DomainException(BaseGameException):
    pass

class InfrastructureException(BaseGameException):
    pass

class ValidationException(BaseGameException):
    pass
