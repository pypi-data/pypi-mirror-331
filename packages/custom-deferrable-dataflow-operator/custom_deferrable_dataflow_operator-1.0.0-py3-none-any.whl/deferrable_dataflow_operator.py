from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context
from airflow.triggers.base import StartTriggerArgs


class DeferrableDataflowOperator(BaseOperator):

    start_trigger_args = StartTriggerArgs(
        trigger_cls="dataflow_trigger.DataflowTrigger",
        trigger_kwargs={},
        next_method="execute_complete",
        next_kwargs=None,
        timeout=None,
    )

    def __init__(
        self,
        *args: list[Any],
        trigger_kwargs: dict[str, Any] | None,
        start_from_trigger: bool,
        end_from_trigger: bool,
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(*args, **kwargs)
        self.start_trigger_args.trigger_kwargs = trigger_kwargs
        self.start_from_trigger = start_from_trigger
        self.end_from_trigger = end_from_trigger

    def execute_complete(self, context: Context, event: dict):
        if event["status"] == "success":
            self.log.info(
                f"Dataflow job started successfully! Job ID: {event['jobId']}")
        else:
            raise RuntimeError(f"Dataflow job failed: {event['message']}")
