import requests

from cruxctl.common.utils.api_utils import (
    get_control_plane_url,
    get_api_headers,
    raise_for_status,
)

DEFAULT_API_TIMEOUT_SECONDS: int = 10


class LogsHandler:
    @staticmethod
    def get_logs(
        profile: str,
        api_token: str,
        dataset_id: str,
        service: str,
        export_id: str,
        execution_date: str,
        delivery_id: str,
        cdu_id: str,
        page_token: str,
        page_size: int,
    ) -> dict:
        """
        Calls the control plane API to run a DAG for a dataset.

        :param profile: the Application Profile
        :param api_token: the API Bearer token
        :param dataset_id: ID of the dataset to get logs for
        :param service: optional Service name to retrieve logs for
        :param export_id: optional Export ID
        :param execution_date: optional Execution Date
        :param delivery_id: optional Delivery ID
        :param cdu_id: optional CDU ID
        :param page_token: optional page token for next page of logs
        :param page_size: optional page size for logs
        """
        base_url: str = get_control_plane_url(profile)
        url: str = f"{base_url}/datasets/{dataset_id}/logs"

        headers: dict = get_api_headers(api_token)

        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            timeout=DEFAULT_API_TIMEOUT_SECONDS,
            json={
                "datasetId": dataset_id,
                "serviceType": service.upper(),
                "exportId": export_id,
                "executionDate": execution_date,
                "deliveryId": delivery_id,
                "cduId": cdu_id,
                "pageToken": page_token,
                "pageSize": page_size,
                "orderBy": "timestamp desc",
            },
        )

        raise_for_status(response)
        return response.json()
