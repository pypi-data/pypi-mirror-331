from abc import abstractmethod
from typing import Tuple

from tensorflow import Tensor
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class Map(DatasetOperation):
    """
    .. _Map:
    Base class for mapping operations.

    Wraps the `Tensorflow Map`_ operation on the dataset.
    Transformations should be implemented in the ``map`` method.

    .. _Tensorflow Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map
    """

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            self.map,
            name=self.__class__.__name__,
        )

    @abstractmethod
    def map(self, *args: Tensor) -> Tuple[Tensor, ...]:
        """
        Implement your transformation in this method.
        The method receives an element of the dataset as input and should return the transformed elements.
        You can change the arguments of this method to retrieve the inner element of tuples if your dataset elements are tuples.
        Example: ``map(self, x: int, y:int) -> int``

        :param args: the dataset element.
        :return: the transformed element.
        """
