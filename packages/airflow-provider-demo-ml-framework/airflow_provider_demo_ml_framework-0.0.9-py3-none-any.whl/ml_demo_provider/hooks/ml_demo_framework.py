from typing import Any
from typing import Dict
import mlflow
from airflow import AirflowException
from airflow.hooks.base import BaseHook

from ml_demo_provider import get_provider_info
from ml_demo_provider.operators.ml.dataset_storage_minio import MinioDatasetStorage


class DatasetStorageHook(BaseHook):
    """
    A hook that interacts with Minio via its Python API library.

    :param dataset_storage_conn_id: Connection ID, defaults to `dataset_storage_default`
    :type dataset_storage_conn_id: str, optional
    """

    conn_name_attr = 'dataset_storage_conn_id'
    default_conn_name = 'dataset_storage_default'
    conn_type = 'http'
    hook_name = 'ML_DEMO_Storage'

    @staticmethod
    def get_connection_form_widgets() -> Dict[str, Any]:
        """Returns connection widgets to add to connection form."""
        from flask_appbuilder.fieldwidgets import BS3PasswordFieldWidget
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import PasswordField
        from wtforms import StringField

        return {
            "extra__http__endpoint": StringField(
                lazy_gettext('Minio endpoint URL'),
                widget=BS3TextFieldWidget(),
                default='localhost:9000',
            ),
            "extra__http__api_key": PasswordField(
                lazy_gettext('API Key'), widget=BS3PasswordFieldWidget()
            ),
        }

    @staticmethod
    def get_ui_field_behaviour() -> Dict:
        """Returns custom field behaviour."""
        return {
            "hidden_fields": ['schema', 'extra'],
            "relabeling": {},
            "placeholders": {
                'extra__http__endpoint': 'localhost:9000',
                'extra__http__api_key': 'your-api-key',
            },
        }

    def __init__(
        self,
        dataset_storage_conn_id: str = default_conn_name,
    ) -> None:
        super().__init__()
        self.dataset_storage_conn_id = dataset_storage_conn_id

    def get_conn(self):
        """Initializes a DatasetStorage client instance."""
        conn = self.get_connection(self.dataset_storage_conn_id)

        self.log.info("Initialize Minio Client")

        storage = MinioDatasetStorage(
            endpoint=conn.host + ":" + str(conn.port),
            access_key=conn.login,
            secret_key=conn.password,
            secure=False,  # Set to True for HTTPS
        )
        # Set MLflow tracking URI TODO: fix configurable port
        try:
            self.log.info("Set MLflow tracking URI:")
            endpoint = conn.extra_dejson.get('endpoint', '')
            self.log.info(endpoint)
            endpoint = conn.extra_dejson.get('extra__http__endpoint', endpoint)
            self.log.info(endpoint)
            mlflow.set_tracking_uri(endpoint)
            self.log.info("MLflow Tracking URI:" + mlflow.get_tracking_uri())
            self.log.info("Set MLflow tracking URI: Done")
        except:
            self.log.info("Error setting MLflow tracking URI")
        return storage

    def run(self) -> Any:
        return self.get_conn()

    def test_connection(self):
        """Test HTTP Connection"""
        try:
            self.run()
            return True, 'Connection successfully tested'
        except Exception as e:
            return False, str(e)
