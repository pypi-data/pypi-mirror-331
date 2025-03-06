from abc import abstractmethod

from tensorflow import Tensor
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class FlatMap(DatasetOperation):
    """
    Base class for flat mapping opertaions.

    Wraps the `Tensorflow Flat Map`_ operation on the dataset.
    Transformations should be implemented in the ``flatmap`` method.

    .. _Tensorflow Flat Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#flat_map
    """

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.flat_map(self.flatmap, name=self.__class__.__name__)

    @abstractmethod
    def flatmap(self, *args: Tensor) -> Dataset:
        """
        Implement your transformation in this method.
        The method receives element an element of the dataset as input and should return a new dataset.
        All new datasets returned by this method are flattened together.
        You can change the arguments of this method to retrieve the inner element of tuples if your dataset elements are tuples.
        Example: ``map(self, x: int, y:int) -> int``

        :param args: the dataset element.
        :return: a new dataset
        """
