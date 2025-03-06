from typing import Callable, Tuple, Union, Any

from tensorflow import DType, Tensor, py_function
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class PythonFunctionLambdaMap(DatasetOperation):
    """
    Base class for inline mapping operations with arbitrary python code.

    Wraps the `Tensorflow Map`_ operation on the dataset where the filter function is wrapped in `py_function`_.
    The return type of the operation must be specified in advance for Tensorflow to build the computation graph.
    For short operations, this class can be used to avoid subclassing :ref:`PythonFunctionMap <PythonFunctionMap>`.
    Transformations should be implemented in the ``map`` constructor parameter.
    This operation should be used when your mapping can not be implemented in with Tensorflow operations.
    For example, if it needs to call an external library.

    :param out_type: The return type of the operation

    .. _Tensorflow Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map
    .. _py_function: https://www.tensorflow.org/api_docs/python/tf/py_function
    """

    def __init__(
        self, out_type: Union[DType, Tuple[DType, ...]], map: Callable[..., Any]
    ):
        self.out_type = out_type
        self.map = map

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            self.adapted_function,
            name=self.__class__.__name__,
        )

    def adapted_function(self, *args: Tensor):
        ls_args = list(args)
        return py_function(
            self.map,
            ls_args,
            self.out_type,
            self.__class__.__name__,
        )
