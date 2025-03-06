from abc import abstractmethod
from typing import Tuple, Union

from tensorflow import DType, Tensor, numpy_function
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class NumpyMap(DatasetOperation):
    """
    .. _NumpyMap:
    Base class for mapping operations that require numpy arrays.

    Wraps the `Tensorflow Map`_ operation on the dataset where the filter function is wrapped in `numpy_function`_.
    The return type of the operation must be specified in advance for Tensorflow to build the computation graph.
    Transformations should be implemented in the ``map`` method.
    This operation is useful if your mapping can not be implemented in with Tensorflow operations, for instance, if it needs to call an external library.

    :param out_type: The return type of the operation
    :param stateful: Whether the operation is stateless. Tensorflow can enable some optimizations on stateless functions to improve performance.

    .. _Tensorflow Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map
    .. _numpy_function: https://www.tensorflow.org/api_docs/python/tf/numpy_function
    """

    def __init__(
        self, out_type: Union[DType, Tuple[DType, ...]], stateful: bool = False
    ):
        self.out_type = out_type
        self.stateful = stateful

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            self._adapted_function,
            name=self.__class__.__name__,
        )

    def _adapted_function(self, *args: Tensor):
        ls_args = list(args)
        return numpy_function(
            self.map,
            ls_args,
            self.out_type,
            self.stateful,
            self.__class__.__name__,
        )

    @abstractmethod
    def map(self, *args: Tensor) -> Tuple[Tensor]:
        """
        Implement your transformation in this method.
        The method receives a dataset element as input transformed into a `numpy ndarray`_ and should return a list of `numpy ndarray`_ .
        The implementation of the transformation can be arbitrary Python code.

        :param args: the dataset element as a `numpy ndarray`_
        :return: the transformed element as a list of `numpy ndarray`_

        .. _numpy ndarray: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html
        """
