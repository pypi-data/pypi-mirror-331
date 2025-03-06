from typing import Callable, Tuple, Union
from tensorflow import Tensor
from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class LambdaMap(DatasetOperation):
    """
    Class for inline mapping operations.

    Wraps the `Tensorflow Map`_ operation on the dataset.
    For short operations, this class can be used to avoid subclassing :ref:`Map <Map>`.
    Transformations should be implemented in the ``map`` constructor parameter.

    .. _Tensorflow Map: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map

    :param map: lambda function implementing the transformation.
    """

    def __init__(self, map: Callable[[...], Union[Tensor, Tuple[Tensor, ...]]]):
        self.map = map

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.map(self.map, name=(self.__class__.__name__,))
