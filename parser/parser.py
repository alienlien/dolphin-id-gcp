import abc
from typing import List
import region


class Parser(abc.ABC):
    @abc.abstractmethod
    def read(self) -> List[region.Region]:
        pass

    @abc.abstractmethod
    def write(self, regions: List[region.Region]) -> None:
        pass
