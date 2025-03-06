from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


DatasetType = type(Dataset)


class Skip(DatasetOperation):
    """
    Dataset skip operation.

    Wraps the `Tensorflow Skip`_ operation on the dataset.
    Skips a given `count` of elements from the dataset.

    :param count: the number of elements to skip

    .. _Tensorflow Skip: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#skip
    """

    def __init__(self, count: int):
        self.count = count

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.skip(self.count, self.__class__.__name__)
