from typing import Any
from typing import Dict
from typing import Iterable

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%s"


class DeployModelOperator(BaseOperator):
    """ """

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
