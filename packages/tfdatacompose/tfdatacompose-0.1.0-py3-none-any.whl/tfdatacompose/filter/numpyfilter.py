from abc import abstractmethod

from numpy import ndarray
from tensorflow import Tensor, numpy_function
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class NumpyFilter(DatasetOperation):
    """
    Base class for filtering operations that require numpy arrays.

    Wraps the `Tensorflow Filter`_ operation on the dataset where the filter function is wrapped in `numpy_function`_.
    The filtering operation should be implemented in the ``filter`` method.
    This operation is useful if your filtering can not be implemented in with Tensorflow operations, for instance, if it needs to call an external library.

    :param stateful: Whether the operation is stateless. Tensorflow can enable some optimizations on stateless functions to improve performance.

    .. _Tensorflow Filter: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#filter
    .. _numpy_function: https://www.tensorflow.org/api_docs/python/tf/numpy_function
    """

    def __init__(self, stateful: bool = False) -> None:
        super().__init__()
        self.stateful: bool = stateful

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.filter(self._adapted_function, name=self.__class__.__name__)

    def _adapted_function(self, *args: Tensor):
        ls_args = list(args)
        return numpy_function(
            self.filter,
            ls_args,
            bool,
            self.stateful,
            self.__class__.__name__,
        )

    @abstractmethod
    def filter(self, *args: ndarray) -> bool:
        """
        Implement your filter in this method.
        The method receives a dataset element as input transformed into a `numpy ndarray`_ and should return a boolean.
        The implementation of the filter can be arbitrary Python code.

        :param args: the dataset element as a `numpy ndarray`_
        :return: ``True`` to keep an element and ``False`` to remove it

        .. _numpy ndarray: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html
        """
