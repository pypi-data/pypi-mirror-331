import depoc
import click
import sys

from .utils._response import _handle_response
from .utils._format import _format_response


client = depoc.DepocClient()


@click.group
def account() -> None:
    ''' Manage user account '''
    pass

@account.command
@click.option('--name')
@click.option('--email')
@click.option('--username')
def update(name: str, email: str, username: str) -> None:
    data = {}
    data.update({'name': name}) if name else None
    data.update({'email': email}) if email else None
    data.update({'username': username}) if username else None

    service = client.accounts.update

    if obj := _handle_response(service, data):
        _format_response(obj, obj.name, f'@{obj.username}')

@account.command
def delete() -> None:
    service = client.accounts.delete

    while True:
        prompt = click.style('Proceed to deletion? [y/n] ', fg='red')
        confirmation = input(prompt)
        if confirmation == 'n':
            sys.exit(0)
        elif confirmation == 'y':
            break

    if obj := _handle_response(service):
        _format_response(obj, 'DEACTIVATED', 'Done', color='red')
