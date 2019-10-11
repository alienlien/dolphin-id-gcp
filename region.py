import attr
import logging

LOGGER = logging.getLogger(__name__)


def get_relative_val(
    v: int, base: int, logger: logging.Logger = LOGGER
) -> float:
    if base == 0:
        logger.warn("Base length is zero")
        return 0.0

    return min(float(v) / float(base), 1.0)


@attr.s
class ImageFile():
    path = attr.ib(type=str)
    x_size = attr.ib(type=int)
    y_size = attr.ib(type=int)


@attr.s
class Label():
    ku_id = attr.ib(type=int)
    group_id = attr.ib(type=int)


@attr.s
class Region():
    file = attr.ib(type=ImageFile)
    shape = attr.ib(type=str)
    x_min = attr.ib(type=int)
    y_min = attr.ib(type=int)
    x_length = attr.ib(type=int)
    y_length = attr.ib(type=int)
    label = attr.ib(type=Label)

    @property
    def x_max(self) -> int:
        return self.x_min + self.x_length

    @property
    def y_max(self) -> int:
        return self.y_min + self.y_length

    def x_min_rel(self) -> float:
        return get_relative_val(self.x_min, self.file.x_size)

    def y_min_rel(self) -> float:
        return get_relative_val(self.y_min, self.file.y_size)

    def x_max_rel(self) -> float:
        return get_relative_val(self.x_max, self.file.x_size)

    def y_max_rel(self) -> float:
        return get_relative_val(self.y_max, self.file.y_size)
