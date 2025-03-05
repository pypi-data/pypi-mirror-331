from typing import Any, List
from typing import Dict
from typing import Iterable

import joblib
import pandas as pd
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from cloudpickle import cloudpickle
from mlflow_provider.hooks.client import MLflowClientHook
import mlflow

from ml_demo_provider.hooks.ml_demo_framework import DatasetStorageHook
from ml_demo_provider.operators.ml.model_trainer import ModelTrainerBuilder

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


class TrainModelOperator(BaseOperator):
    """
    Training a model and return trained Model ID of stored artifact.
    :param experiment_name: Name of the experiment to track.
    :type experiment_name: str
    :param model_type: type of ML Model to Train.
    :type model_type: str
        ...
    :param dataset_storage_conn_id: Connection ID, defaults to `dataset_storage_default`
    :type dataset_storage_conn_id: str, optional
    :return: Dataset Storage ID
    :rtype: str
    """

    # Specify the arguments that are allowed to parse with jinja templating
    template_fields: Iterable[str] = [
        "model_type",
        "train_dataset_name",
        "train_dataset_id",
        "target",
        "features_list",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a480'

    def __init__(
        self,
        *,
        model_type: str = None,
        train_dataset_name: str = None,
        train_dataset_id: str = None,
        target: str = None,
        features_list: List[str] = None,
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model_type = model_type
        self.train_dataset_name = train_dataset_name
        self.train_dataset_id = train_dataset_id
        self.features_list = features_list
        self.target = target
        self.dataset_storage_conn_id = dataset_storage_conn_id

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Storage client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        # load train dataset from storage
        train_data = storage_client.load_dataframe(
            dataset_name=self.train_dataset_name, version=self.train_dataset_id
        )

        experiment_name = context["params"]["experiment_name"]

        # Create and train model with MLflow tracking
        model_trainer_builder = ModelTrainerBuilder()
        trainer = model_trainer_builder.create_model_trainer(
            model_type=self.model_type,
            train_data=train_data,
            mlflow_experiment_name=experiment_name,
            target=self.target,
            features=self.features_list,
        )

        # Train the model
        model, metrics, model_id = trainer.train()

        # TODO: add model performance to the operator output
        # Print model performance
        print("\nModel performance:")
        for metric_name, metric_value in metrics.items():
            print(f"  {metric_name}: {metric_value:.4f}")

        return model_id


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
