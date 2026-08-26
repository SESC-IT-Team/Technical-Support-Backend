from enum import Enum

# change values to russian and real ones?
class Status(Enum):
    DONE = "done"
    IN_PROGRESS = "in progress"
    NOT_STARTED = "not started"

class OrdersQuery(Enum):
    ALL = "all"
    TODO = "todo"
    MY = "my"