from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class Batch(DatasetOperation):
    """
    Dataset batching operation.

    Wraps the `Tensorflow Batch`_ operation on the dataset.
    Makes batches of size `batch_size` from the dataset.

    :param batch_size: the size of the batch
    :param drop_remainder: drop the last elements if there's not enough to make a batch

    .. _Tensorflow Batch: https://www.tensorflow.org/api_docs/python/tf/data/Dataset#batch
    """

    def __init__(self, batch_size: int, drop_remainder: bool):
        self.batch_size = batch_size
        self.drop_remainder = drop_remainder

    def apply(self, dataset: Dataset) -> Dataset:
        return dataset.batch(
            self.batch_size,
            self.drop_remainder,
            name=self.__class__.__name__,
        )
