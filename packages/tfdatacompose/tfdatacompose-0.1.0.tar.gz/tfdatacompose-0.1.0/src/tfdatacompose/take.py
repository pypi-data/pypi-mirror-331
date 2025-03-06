from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class Take(DatasetOperation):
    """
    Dataset take operation.

    Wraps the `Tensorflow Take`_ operation on the dataset.
    Creates a new dataset by taking `count` element from the dataset.

    :param count: the number of elements to take from the original dataset

    .. _Tensorflow Take: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#take
    """

    def __init__(self, count: int):
        self.count = count

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.take(self.count, self.__class__.__name__)
