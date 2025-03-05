from typing import Any
from typing import Dict
from typing import Iterable

import pandas as pd
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator

from ml_demo_provider.hooks.ml_demo_framework import DatasetStorageHook


class LoadDatasetOperator(BaseOperator):
    """
    Uploading local file to Dataset Storage and return Dataset ID.
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
        "dataset_name",
        "file_path",
        "file_path_param",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        dataset_name: str = None,
        file_path: str = None,
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset_name = dataset_name
        self.list_ids = list_ids
        self.file_path = file_path
        self.file_path_param = file_path_param
        self.dataset_storage_conn_id = dataset_storage_conn_id
        if kwargs.get('xcom_push') is not None:
            raise AirflowException(
                "'xcom_push' was deprecated, use 'BaseOperator.do_xcom_push' instead"
            )

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Storage client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        if self.file_path is None:
            self.file_path = context["params"][self.file_path_param]

        df = pd.read_csv(self.file_path)

        # Save dataframe with metadata
        dataset_id = storage_client.save_dataframe(
            dataset_name=self.dataset_name,
            df=df,
            # TODO: get metadata from params
            metadata={
                "description": "Sample dataset for testing",
                "author": "Data Science Team",
                "source": "test data",
            },
        )
        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id  # TODO: extend output with methadata {"dataset": dataset_id, ...}


class DownloadDatasetOperator(BaseOperator):
    """
    Uploading local file to Dataset Storage and return Dataset ID.
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
        "dataset_name",
        "dataset_id",
        "file_path",
        "file_path_param",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        dataset_name: str = None,
        dataset_id: str = None,
        file_path: str = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset_name = dataset_name
        self.dataset_id = dataset_id
        self.file_path = file_path
        self.file_path_param = file_path_param
        self.dataset_storage_conn_id = dataset_storage_conn_id

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Storage client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        # Save dataframe with metadata
        customers_df = storage_client.load_dataframe(
            dataset_name=self.dataset_name,
            version=self.dataset_id,
        )
        customers_df.to_csv(self.file_path, index=False)
        print(f"Saved dataset with version: {self.dataset_id}")
        self.log.info(f"Dataset created: dataset_id={self.dataset_id}")
        return self.dataset_id
