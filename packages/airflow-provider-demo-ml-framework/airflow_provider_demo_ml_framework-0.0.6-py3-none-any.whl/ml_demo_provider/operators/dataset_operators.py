from typing import Any
from typing import Dict
from typing import Iterable

import joblib
import pandas as pd
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from mlflow_provider.hooks.client import MLflowClientHook

from ml_demo_provider.hooks.ml_demo_framework import DatasetStorageHook
from ml_demo_provider.operators.ml.model_trainer import ModelTrainerBuilder


class CombineDatasetsOperator(BaseOperator):
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
        "dataset1_name",
        "dataset2_name",
        "dataset1_id",
        "dataset2_id",
        "output_dataset_name",
        "file_path",
        "file_path_param",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        dataset1_name: str = None,
        dataset2_name: str = None,
        dataset1_id: str = None,
        dataset2_id: str = None,
        output_dataset_name: str = None,
        file_path: str = None,
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset1_name = dataset1_name
        self.dataset2_name = dataset2_name
        self.dataset1_id = dataset1_id
        self.dataset2_id = dataset2_id
        self.output_dataset_name = output_dataset_name
        self.list_ids = list_ids
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

        mlflow_client = MLflowClientHook(mlflow_conn_id="mlflow_default")

        # Save dataframe with metadata
        customers_df = storage_client.load_dataframe(
            dataset_name=self.dataset1_name, version=self.dataset1_id
        )

        noncustomers_df = storage_client.load_dataframe(
            dataset_name=self.dataset2_name, version=self.dataset2_id
        )

        # customers_df = pd.read_csv('/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/customers.csv')
        # noncustomers_df = pd.read_csv('/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/noncustomers.csv')

        preprocess_data_transform_func = joblib.load(
            "/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/preprocess_data_transform.pkl"
        )

        df_transformed = preprocess_data_transform_func(customers_df, noncustomers_df)

        # print(self.list_ids)
        # # Create a sample dataframe
        # # df = pd.DataFrame({
        # #     'id': range(1, 101),
        # #     'value': [i * 2 for i in range(1, 101)],
        # #     'category': ['A' if i % 2 == 0 else 'B' for i in range(1, 101)]
        # # })
        # df = pd.read_csv(self.file_path)

        # Save dataframe with metadata
        dataset_id = storage_client.save_dataframe(
            dataset_name=self.output_dataset_name,
            df=df_transformed,
            metadata={
                "description": "Sample dataset for testing",
                "author": "Data Science Team",
                "source": "test data",
            },
        )
        print(f"Saved dataset with version: {dataset_id}")
        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id  # {"dataset": dataset_id}


class TransformDatasetOperator(BaseOperator):
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
        "output_dataset_name",
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
        output_dataset_name: str = None,
        file_path: str = None,
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset_name = dataset_name
        self.output_dataset_name = output_dataset_name
        self.list_ids = list_ids
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
        customers_df = storage_client.load_dataframe(dataset_name=self.dataset_name, version=None)

        # customers_df = pd.read_csv('/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/customers.csv')
        noncustomers_df = pd.read_csv(
            '/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/noncustomers.csv'
        )

        preprocess_data_transform_func = joblib.load(
            "/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/preprocess_data_transform.pkl"
        )

        df_transformed = preprocess_data_transform_func(customers_df, noncustomers_df)

        # print(self.list_ids)
        # # Create a sample dataframe
        # # df = pd.DataFrame({
        # #     'id': range(1, 101),
        # #     'value': [i * 2 for i in range(1, 101)],
        # #     'category': ['A' if i % 2 == 0 else 'B' for i in range(1, 101)]
        # # })
        # df = pd.read_csv(self.file_path)

        # Save dataframe with metadata
        dataset_id = storage_client.save_dataframe(
            dataset_name=self.output_dataset_name,
            df=df_transformed,
            metadata={
                "description": "Sample dataset for testing",
                "author": "Data Science Team",
                "source": "test data",
            },
        )
        print(f"Saved dataset with version: {dataset_id}")
        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id  # {"dataset": dataset_id}


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
        # Initialize Minio client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        print(self.list_ids)
        # Create a sample dataframe
        # df = pd.DataFrame({
        #     'id': range(1, 101),
        #     'value': [i * 2 for i in range(1, 101)],
        #     'category': ['A' if i % 2 == 0 else 'B' for i in range(1, 101)]
        # })
        df = pd.read_csv(self.file_path)

        # Save dataframe with metadata
        dataset_id = storage_client.save_dataframe(
            dataset_name=self.dataset_name,
            df=df,
            metadata={
                "description": "Sample dataset for testing",
                "author": "Data Science Team",
                "source": "test data",
            },
        )
        print(f"Saved dataset with version: {dataset_id}")
        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id  # {"dataset": dataset_id}


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
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset_name = dataset_name
        self.dataset_id = dataset_id
        self.list_ids = list_ids
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
        customers_df = storage_client.load_dataframe(
            dataset_name=self.dataset_name,
            # version=self.dataset_id,
        )
        customers_df.to_csv(self.file_path, index=False)
        print(f"Saved dataset with version: {self.dataset_id}")
        self.log.info(f"Dataset created: dataset_id={self.dataset_id}")
        return self.dataset_id


class TrainModelOperator(BaseOperator):
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
        "train_dataset_name",
        "train_dataset_id",
        "file_path",
        "file_path_param",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        train_dataset_name: str = None,
        train_dataset_id: str = None,
        file_path: str = None,
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.train_dataset_name = train_dataset_name
        self.train_dataset_id = train_dataset_id
        self.list_ids = list_ids
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

        mlflow_client = MLflowClientHook(mlflow_conn_id="mlflow_default")

        # Save dataframe with metadata
        train_data = storage_client.load_dataframe(
            dataset_name=self.train_dataset_name, version=self.train_dataset_id
        )

        # Define features and target
        features = [
            'active_days',
            'month1_total_actions',
            'month1_deals_actions',
            'object_types_used',
            'two_weeks_delta',
        ]

        target = 'is_customer'

        # Create and train a Random Forest classifier with MLflow tracking
        model_trainer_builder = ModelTrainerBuilder()
        trainer = model_trainer_builder.create_model_trainer(
            model_type='logistic',
            train_data=train_data,
            mlflow_experiment_name='customer_transition_prediction',
            target=target,
            features=features,
        )

        # Train the model
        model, metrics, model_id = trainer.train()

        # Print model performance
        print("\nModel performance:")
        for metric_name, metric_value in metrics.items():
            print(f"  {metric_name}: {metric_value:.4f}")

        # preprocess_data_transform_func = joblib.load(
        #     "/Users/oleksandr/development/hubspot-demo-ml-pipeline/datasets/preprocess_data_transform.pkl")
        #
        # df_transformed = preprocess_data_transform_func(customers_df, noncustomers_df)

        return model_id


class BatchPredictionOperator(BaseOperator):
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
        "input_dataset_name",
        "input_dataset_id",
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
        file_path: str = None,
        list_ids: dict = None,
        file_path_param: str = "dataset_file_path",
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.input_dataset_name = input_dataset_name
        self.input_dataset_id = input_dataset_id
        self.list_ids = list_ids
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

        mlflow_client = MLflowClientHook(mlflow_conn_id="mlflow_default")

        # Save dataframe with metadata
        train_data = storage_client.load_dataframe(
            dataset_name=self.train_dataset_name, version=self.train_dataset_id
        )

        # Define features and target
        features = [
            'active_days',
            'month1_total_actions',
            'month1_deals_actions',
            'object_types_used',
            'two_weeks_delta',
        ]

        return "model_id"
