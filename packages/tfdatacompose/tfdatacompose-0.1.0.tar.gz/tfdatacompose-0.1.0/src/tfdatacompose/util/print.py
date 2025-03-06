from typing import Tuple

import tensorflow
from tensorflow import Tensor

from tfdatacompose.map.map import Map


class Print(Map):
    """
    Print tensor operation.

    Prints the dataset element, then forwards the elements unchanged.
    This operation is mainly used for debugging.

    :param name: The name of the operation to display when printing, if None a number is displayed instead.
    """

    number = 1

    def __init__(self, name: str | None = None):
        if name is None:
            self.name = Print.number
            Print.number += 1
        else:
            self.name = name

    def map(self, *args) -> Tuple[Tensor, ...]:
        tensorflow.print(f"Print:{self.name}", *args)
        return args
