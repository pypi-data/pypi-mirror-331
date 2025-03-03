import click

from typing import Any

from depoc.objects.base import DepocObject
from depoc.utils._error import APIError


def _handle_response(
        service: Any,
        data: dict[str, Any] | None = None,
        resource_id: str | None = None,
        **params,
    ) -> DepocObject | None:
    try:
        if data and resource_id:
            response = service(data, resource_id)
        elif data:
            response = service(data)
        elif resource_id:
            response = service(resource_id)
        else:
            response = service(**params)
        return response
    except APIError as e:
        click.echo(str(e))
    return None
