import tensorflow
from tensorflow import Tensor, shape

from tfdatacompose.map.map import Map


class PrintShape(Map):
    """
    Print tensor shape operation.

    Prints the dataset element's shape, then forwards the elements unchanged.
    This operation is mainly used for debugging.

    :param name: The name of the operation to display when printing, if None a number is displayed instead.
    """

    number = 1

    def __init__(self, name: str | None = None):
        if name is None:
            self.name = PrintShape.number
            PrintShape.number += 1
        else:
            self.name = name

    def map(self, *args: Tensor) -> tuple[Tensor, ...]:
        shapes = (shape(a) for a in args)
        tensorflow.print(f"PrintShape:{self.name}", *shapes)
        return args
