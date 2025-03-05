import depoc
import click

from .utils._response import _handle_response
from .utils._format import _format_response


client = depoc.DepocClient()


@click.group
def contact() -> None:
    ''' Contacts - retrieve all and filter. '''
    pass

@contact.command
@click.option('-l', '--limit', default=50)
@click.option('-p', '--page', default=0)
@click.option('-d', '--detailed', is_flag=True)
def all(limit: int, page: int, detailed: bool) -> None:
    ''' Retrieve all contacts. '''
    service = client.contacts.all

    if response := _handle_response(service, limit=limit, page=page):
        click.echo(f'\nResults: {response.count}')
        if limit < response.count:
            click.echo(
                f'Showing: {len(response.results)} out of {response.count}'
            ) 
        if response.next:
            click.echo(f'For next page: --page <number>')

        for obj in response.results:
            if hasattr(obj, 'customer'):
                title = f'{obj.customer.name}'
                header = 'customer'
                highlight = obj.customer.alias
                obj = obj.customer
            elif hasattr(obj, 'supplier'):
                title = f'\n{obj.supplier.legal_name}'
                header = 'supplier'
                highlight = obj.supplier.trade_name
                obj = obj.supplier
            
            remove = [] if detailed else \
            [item for item in obj.to_dict().keys() if item != 'id']

            _format_response(obj, title, header, highlight, remove=remove)


@contact.command
@click.option('-s', '--search')
@click.option('-l', '--limit', default=50)
@click.option('-d', '--detailed', is_flag=True)
def filter(search: str, limit: int, detailed: bool) -> None:
    ''' Filter contacts. '''
    service = client.contacts.filter

    if response := _handle_response(service, search=search, limit=limit):
        click.echo(f'\nResults: {response.count}')
        if limit < response.count:
            click.echo(
                f'Showing: {len(response.results)} out of {response.count}'
            ) 
        if response.next:
            click.echo(f'For next page: --page <number>')

        for obj in response.results:
            if hasattr(obj, 'customer'):
                title = f'\n{obj.customer.name}'
                header = 'customer'
                highlight = obj.customer.alias
                obj = obj.customer
            elif hasattr(obj, 'supplier'):
                title = f'\n{obj.supplier.legal_name}'
                header = 'supplier'
                highlight = obj.supplier.trade_name
                obj = obj.supplier
            
            remove = [] if detailed else \
            [item for item in obj.to_dict().keys() if item != 'id']
            
            _format_response(obj, title, header, highlight, remove=remove)
