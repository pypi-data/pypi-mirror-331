from typing import List

from tensorflow.python.data import Dataset

from tfdatacompose.datasetoperation import DatasetOperation


class Pipeline(DatasetOperation):
    """
    Composite of Dataset Operations.

    Takes a list of Dataset Operations and executes them in order.
    A pipeline is a dataset operation, therefore, it can be reused in other pipelines.

    :param dataset_operations: a list of Dataset Operation
    """

    def __init__(self, dataset_operations: List[DatasetOperation]):
        self.dataset_operations = dataset_operations

    def apply(self, dataset: Dataset) -> Dataset:
        for op in self.dataset_operations:
            try:
                dataset = op.apply(dataset)
            except Exception as e:
                raise PreprocessingException(op.__class__).with_traceback(
                    e.__traceback__
                ) from e

        return dataset


class PreprocessingException(BaseException):
    def __init__(self, operation_name):
        super().__init__(f"Encountered an exception with operation: {operation_name}")
