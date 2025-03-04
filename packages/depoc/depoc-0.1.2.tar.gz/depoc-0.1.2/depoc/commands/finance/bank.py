import depoc
import click

from ..utils._response import _handle_response
from ..utils._format import _format_response


client = depoc.DepocClient()


@click.group
def bank() -> None:
    ''' Manage bank accounts '''
    pass

@bank.command
@click.argument('name')
def create(name: str) -> None:
    ''' Create a new bank account. '''
    data = {'name': name}
    service = client.financial_accounts.create

    if obj := _handle_response(service, data):
            highlight = f'R$ {obj.balance}'
            _format_response(obj, obj.name, highlight)

@bank.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific bank account. '''
    service = client.financial_accounts.get

    if obj := _handle_response(service, resource_id=id):
        highlight = f'R$ {obj.balance}'
        _format_response(obj, obj.name, highlight)

@bank.command
def all() -> None:
    ''' Retrieve all bank accounts. '''
    service = client.financial_accounts.all

    total_balance: float = 0

    if response := _handle_response(service):
        for obj in response.results:
            total_balance += float(obj.balance)
            highlight = f'R$ {obj.balance}'
            remove = ['name', 'balance', 'created_at', 'is_active']
            _format_response(obj, obj.name, highlight, remove=remove)

        format_total_balance = f'R$ {total_balance:.2f}'
        txt = f'\n{'Total Balance: ' + format_total_balance:>50}\n'
        click.echo(txt)

@bank.command
@click.argument('id')
@click.argument('name')
def update(id: str, name: str) -> None:
    ''' Update a bank account. '''
    data = {'name': name}
    service = client.financial_accounts.update

    if obj := _handle_response(service, data, id):
            highlight = f'R$ {obj.balance}'
            _format_response(obj, obj.name, highlight)

@bank.command
@click.argument('id')
def delete(id: str) -> None:
    ''' Delete a bank account. '''
    service = client.financial_accounts.delete

    if obj := _handle_response(service, resource_id=id):
        _format_response(obj, 'DEACTIVATED', 'Done', color='red')
