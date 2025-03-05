from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
import pandas as pd
import dill
import mlflow
from airflow.models import BaseOperator

from ml_demo_provider.hooks.ml_demo_framework import DatasetStorageHook


class MLTransformOperator(BaseOperator):

    def deserialize_with_mlflow(self, run_id, artifact_path):
        """Deserialize a function from MLflow artifacts"""
        import tempfile

        # Get the client
        client = mlflow.tracking.MlflowClient()

        # Create a temporary directory to download artifacts
        temp_dir = tempfile.mkdtemp()
        import pandas as pd
        try:
            # Download the artifact to the temporary directory
            # This downloads the artifact while preserving its relative path
            downloaded_path = client.download_artifacts(run_id, artifact_path, temp_dir)
            print(pd.__version__)
            # Load the function from the downloaded file
            with open(downloaded_path, 'rb') as f:
                func = dill.load(f)

            print(f"Function deserialized from MLflow artifact: {artifact_path}")
            return func

        finally:
            # Clean up - remove the temporary directory and all its contents
            import shutil

            shutil.rmtree(temp_dir)


class TransformDatasetOperator(MLTransformOperator):
    """
    Transform input dataset and return Dataset ID.
    :param dataset_name: The path to the file.
    :type dataset_name: str, optional
    # TODO: add params
    :return: Dataset Storage ID
    :rtype: str
    """

    # Specify the arguments that are allowed to parse with jinja templating
    template_fields: Iterable[str] = [
        "dataset_name",
        "dataset_id",
        "output_dataset_name",
        "artifact_id",
        "version_id",
        "output_dataset_name",
    ]
    template_fields_renderers: Dict[str, str] = {}
    template_ext: Iterable[str] = ()
    ui_color = '#f4a460'

    def __init__(
        self,
        *,
        dataset_name: str,
        dataset_id: str,
        artifact_id: str,
        version_id: str = None,
        output_dataset_name: str = None,
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset_name = dataset_name
        self.dataset_id = dataset_id
        self.artifact_id = artifact_id
        self.version_id = version_id
        self.output_dataset_name = output_dataset_name
        self.dataset_storage_conn_id = dataset_storage_conn_id

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Storage client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        input_df = storage_client.load_dataframe(
            dataset_name=self.dataset_name, version=self.dataset_id
        )
        import pandas as pd
        with mlflow.start_run(run_id=None, nested=True):
            loaded_func_calculate_rolling_features = self.deserialize_with_mlflow(
                self.version_id, artifact_path=self.artifact_id
            )

        df_transformed = loaded_func_calculate_rolling_features(input_df)

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
        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id


class CombineDatasetsOperator(MLTransformOperator):
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
        "artifact_id",
        "version_id",
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
        artifact_id: str = None,
        version_id: str = None,
        output_dataset_name: str = None,
        dataset_storage_conn_id: str = "dataset_storage_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.dataset1_name = dataset1_name
        self.dataset2_name = dataset2_name
        self.dataset1_id = dataset1_id
        self.dataset2_id = dataset2_id
        self.artifact_id = artifact_id
        self.version_id = version_id
        self.output_dataset_name = output_dataset_name
        self.dataset_storage_conn_id = dataset_storage_conn_id

    def execute(self, context: Dict[str, Any]) -> str:
        # Initialize Storage client
        storage_client = DatasetStorageHook(
            dataset_storage_conn_id=self.dataset_storage_conn_id
        ).run()

        input_df1 = storage_client.load_dataframe(
            dataset_name=self.dataset1_name, version=self.dataset1_id
        )
        input_df2 = storage_client.load_dataframe(
            dataset_name=self.dataset2_name, version=self.dataset2_id
        )
        import pandas as pd
        with mlflow.start_run(run_id=None, nested=True):
            loaded_func_calculate_rolling_features = self.deserialize_with_mlflow(
                self.version_id, artifact_path=self.artifact_id
            )

        df_transformed = loaded_func_calculate_rolling_features(input_df1, input_df2)

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

        self.log.info(f"Dataset created: dataset_id={dataset_id}")
        return dataset_id
