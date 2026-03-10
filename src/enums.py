from enum import Enum

# change values to russian and real ones?
class Status(Enum):
    DONE = "done"
    IN_PROGRESS = "in progress"
    NOT_STARTED = "not started"

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"