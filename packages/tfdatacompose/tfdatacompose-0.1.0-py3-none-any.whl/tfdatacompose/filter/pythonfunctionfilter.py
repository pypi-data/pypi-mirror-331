from abc import abstractmethod

from tensorflow import Tensor, py_function
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class PythonFunctionFilter(DatasetOperation):
    """
    Base class for filtering operations with arbitrary python code.

    Wraps the `Tensorflow Filter`_ operation on the dataset where the filter function is wrapped in `py_function`_.
    The filtering operation should be implemented in the ``filter`` method.
    This operation should be used when your filtering can not be implemented in with Tensorflow operations.
    For instance, if it needs to call an external library.

    .. _Tensorflow Filter: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#filter
    .. _py_function: https://www.tensorflow.org/api_docs/python/tf/py_function
    """

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.filter(self._adapted_function, name=self.__class__.__name__)

    def _adapted_function(self, *args: Tensor):
        ls_args = list(args)
        return py_function(
            self.filter,
            ls_args,
            bool,
            self.__class__.__name__,
        )

    @abstractmethod
    def filter(self, *args) -> bool:
        """
        Implement your filter in this method.
        The method receives a dataset element as `Tensor`_ and should return a boolean.
        The implementation of the filter can be arbitrary Python code.

        :param args: the dataset element as a `Tensor`_
        :return: ``True`` to keep an element and ``False`` to remove it

        .. _Tensor: https://www.tensorflow.org/api_docs/python/tf/Tensor
        """
