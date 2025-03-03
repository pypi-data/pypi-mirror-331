import depoc
import click

from .utils._response import _handle_response
from .utils._format import _format_response


client = depoc.DepocClient()


@click.command
def me() -> None:
    ''' Get the current user's data'''
    service = client.me.get

    if obj := _handle_response(service):
        title = f'Welcome {obj.name}'
        header = f'@{obj.username}'
        _format_response(obj, title, header, obj.email)
