from abc import abstractmethod
from typing import Any, Tuple, Union

from tensorflow import DType, Tensor, py_function
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class PythonFunctionMap(DatasetOperation):
    """
    .. _PythonFunctionMap:
    Base class for mapping operations with arbitrary python code.

    Wraps the `Tensorflow Map`_ operation on the dataset where the filter function is wrapped in `py_function`_.
    The return type of the operation must be specified in advance for Tensorflow to build the computation graph.
    The filtering operation should be implemented in the ``map`` method.
    This operation should be used when your mapping can not be implemented in with Tensorflow operations.
    For example, if it needs to call an external library.

    :param out_type: The return type of the operation

    .. _Tensorflow Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map
    .. _py_function: https://www.tensorflow.org/api_docs/python/tf/py_function
    """

    def __init__(self, out_type: Union[DType, Tuple[DType, ...]]):
        self.out_type = out_type

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            self._adapted_function,
            name=self.__class__.__name__,
        )

    def _adapted_function(self, *args: Tensor):
        ls_args = list(args)
        return py_function(
            self.map,
            ls_args,
            self.out_type,
            self.__class__.__name__,
        )

    @abstractmethod
    def map(self, *args) -> Any:
        """
        Implement your transformation in this method.
        The method receives an element of the dataset as input and should return the transformed elements.
        You can change the arguments of this method to retrieve the inner element of tuples if your dataset elements are tuples.
        Example: ``map(self, x: int, y:int) -> int``
        The implementation for the mapping can be arbitrary Python code.

        :param args: the dataset element as a `Tensor`_
        :return: the transformed element.

        .. _Tensor: https://www.tensorflow.org/api_docs/python/tf/Tensor
        """
