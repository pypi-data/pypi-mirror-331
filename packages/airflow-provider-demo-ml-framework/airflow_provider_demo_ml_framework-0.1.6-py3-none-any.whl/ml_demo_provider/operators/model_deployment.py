from typing import Any
from typing import Dict
from typing import Iterable
from typing import List

import mlflow
import pandas as pd
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator

from ml_demo_provider.hooks.ml_demo_framework import DatasetStorageHook

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%s"


class BatchPredictionOperator(BaseOperator):
    """
    Running predictions on input dataset using ML Model artifact and return Dataset ID with predictions.
    :param dataset_name: The path to the file.
    :type dataset_name: str, optional
    :param file_path: The path to the file.
    :type file_path: str, optional
    :param file_path_param: Name of the parameter in the configuration to use as file_path, defaults to `dataset_file_path`
    :type file_path_param: str, optional
    :param dataset_storage_conn_id: Connection ID, defaults to `dataset_storage_default`
    :type dataset_storage_conn_id: str, optional
    :return: Dataset Storage ID
    :rtype: str
    """

    # Specify the arguments that are allowed to parse with jinja templating
    template_fields: Iterable[str] = [
        "input_dataset_name",
        "input_dataset_id",
        "output_dataset_name",
        "model_id",
        "features_list",
        "file_path",
        "file_path_param",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        input_dataset_name: str = None,
        input_dataset_id: str = None,
        output_dataset_name: str = None,
        model_id: str = None,
        file_path: str = None,
        features_list: List[str] = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.input_dataset_name = input_dataset_name
        self.input_dataset_id = input_dataset_id
        self.output_dataset_name = output_dataset_name
        self.model_id = model_id
        self.features_list = features_list
        self.file_path = file_path
        self.file_path_param = file_path_param
        self.dataset_storage_conn_id = dataset_storage_conn_id
        if kwargs.get('xcom_push') is not None:
            raise AirflowException(
                "'xcom_push' was deprecated, use 'BaseOperator.do_xcom_push' instead"
            )

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Minio client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        # Save dataframe with metadata
        input_data = storage_client.load_dataframe(
            dataset_name=self.input_dataset_name, version=self.input_dataset_id
        )

        # Load model as a PyFuncModel.
        loaded_model = mlflow.pyfunc.load_model(self.model_id)

        # Predict on a Pandas DataFrame.
        input_data['predict'] = loaded_model.predict(input_data[self.features_list])

        # Save dataframe with metadata
        output_dataset_id = storage_client.save_dataframe(
            dataset_name=self.output_dataset_name,
            df=input_data,
            metadata={
                "description": "Sample dataset for testing",
                "author": "Data Science Team",
                "source": "test data",
            },
        )
        return output_dataset_id


class DeployModelOperator(BaseOperator):
    """ """

    # TODO: Implement deployment to KServe
    # Specify the arguments that are allowed to parse with jinja templating
    template_fields: Iterable[str] = ["model_id"]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model_id = model_id
        if kwargs.get('xcom_push') is not None:
            raise AirflowException(
                "'xcom_push' was deprecated, use 'BaseOperator.do_xcom_push' instead"
            )

    def execute(self, context: Dict[str, Any]) -> str:

        return "tst12345"  # deployment.id
