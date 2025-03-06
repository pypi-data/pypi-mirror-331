from abc import ABC, abstractmethod

from tensorflow.python.data import Dataset


class DatasetOperation(ABC):
    """
    Base class for dataset operations.

    Implement the operation on the dataset in the `apply` method.
    """

    @abstractmethod
    def apply(self, dataset: Dataset) -> Dataset:
        """
        Applies the operation on the given dataset and returns the new dataset.

        :param dataset: `Tensorflow Dataset`_
            The dataset to change
        :return: `Tensorflow Dataset`_
            The changed dataset

        .. _Tensorflow Dataset: https://www.tensorflow.org/api_docs/python/tf/data/Dataset
        """
        ...

    def __call__(self, dataset: Dataset) -> Dataset:
        return self.apply(dataset)
