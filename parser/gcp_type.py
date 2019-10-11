from enum import Enum


class GCPImageType(Enum):
    TRAIN = 1
    VALIDATE = 2
    TEST = 3
    UNASSIGNED = 4