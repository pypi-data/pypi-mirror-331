import logging
import clickhouse_connect

from celery import shared_task

from .models import CRUDEvent, LoginEvent
from .serializers import CRUDEventSerializer, LoginEventSerializer
from .settings import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_DATABASE,
)

logger = logging.getLogger(__name__)


@shared_task
def send_logs_to_clickhouse():
    logger.info("Clickhouse: Initiating data transfer...")

    # CRUD Event logs
    crud_logs = CRUDEvent.objects.all()
    crud_serializer = CRUDEventSerializer(crud_logs, many=True)
    crud_row_matrix = []

    for log in crud_serializer.data:
        crud_row_matrix.append(list(log.values()))

    # Login Event logs
    login_logs = LoginEvent.objects.all()
    login_serializer = LoginEventSerializer(login_logs, many=True)
    login_row_matrix = []

    for log in login_serializer.data:
        login_row_matrix.append(list(log.values()))

    logger.info(
        "Clickhouse: Collected %s crud logs and %s login logs",
        len(crud_row_matrix),
        len(login_row_matrix),
    )

    insert_data = {
        "crud_logs": {
            "table": f"{CLICKHOUSE_DATABASE}.audit_crudevent",
            "data": crud_row_matrix,
            "column_names": [
                "event_type",
                "object_id",
                "object_repr",
                "object_json_repr",
                "changed_fields",
                "user_id",
                "user_pk_as_string",
                "created_at",
            ],
            "object": crud_logs,
        },
        "login_logs": {
            "table": f"{CLICKHOUSE_DATABASE}.audit_loginevent",
            "data": login_row_matrix,
            "column_names": [
                "login_type",
                "username",
                "user_id",
                "remote_ip",
                "created_at",
            ],
            "object": login_logs,
        },
    }

    try:
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            secure=True,
        )

        for table, data in insert_data.items():
            if data:
                response = client.insert(
                    data["table"],
                    data["data"],
                    column_names=data["column_names"],
                )

                logger.info(
                    "Clickhouse: %s transfer successful. Row count: (%s)",
                    table,
                    response.written_rows,
                )

                # Delete the data from the database
                # data["object"].delete() # noqa

    except Exception as e:
        logger.error("Clickhouse: Data transfer failed. Error: %s", e)
