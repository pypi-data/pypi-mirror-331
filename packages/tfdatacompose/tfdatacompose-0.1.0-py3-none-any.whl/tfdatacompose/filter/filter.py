from abc import abstractmethod

from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class Filter(DatasetOperation):
    """
    Base class for Filtering operations

    Wraps the `Tensorflow Filter`_ operation on the dataset.
    The filtering operation should be implemented in the ``filter`` method.

    .. _Tensorflow Filter: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#filter
    """

    def apply(self, dataset) -> Dataset:
        return dataset.filter(self.filter, name=self.__class__.__name__)

    @abstractmethod
    def filter(self, *args) -> bool:
        """
        Implement the filtering in this method.
        The method receives an element of the dataset as input and should return a boolean.
        You can change the arguments of this method to retrieve the inner element of tuples if your dataset elements are tuples.
        Example: ``map(self, x: int, y:int) -> bool``

        :param args: the dataset element.
        :return: ``True`` to keep an element and ``False`` to remove it
        """
