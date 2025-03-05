import depoc
import click
import sys
import time

from typing import Any
from datetime import datetime

from ..utils._response import _handle_response
from ..utils._format import _format_response, spinner


client = depoc.DepocClient()


@click.group
def transaction() -> None:
    ''' Manage financial transactions '''
    pass

@transaction.command
@click.option('-c', '--credit', is_flag=True)
@click.option('-d', '--debit', is_flag=True)
@click.option('-t', '--transfer', is_flag=True)
def create(
    credit: bool,
    debit: bool,
    transfer: bool,
) -> None:
    if not any([credit, debit, transfer]):
        message = (
            'Inform a type of transaction: \n'
            '-c (credit), -d (debit) or -t (transfer).'
        )
        click.echo(message)
        sys.exit(0)

    click.echo(f'\n{'ADD NEW TRANSACION':-<50}')

    data: dict[str, Any] = {}
    data.update({'amount': input('Amount: R$')})
    data.update({'account': input('Account ID: ')})
    data.update({'send_to': input('Send to ID: ')}) if transfer else None
    data.update({'description': input('Description: ')})
    data.update({'category': input('Category ID: ')})
    data.update({'contact': input('Contact ID: ')})

    click.echo(f'{'':-<50}')

    if credit:
        data.update({'type': 'credit'})
    elif debit:
        data.update({'type': 'debit'})
    elif transfer:
        data.update({'type': 'transfer'})

    service = client.financial_transactions.create

    if obj := _handle_response(service, data):
        header = f'R$ {obj.amount}'
        title = f'{obj.account.name} {obj.type}'
        timestamp = datetime.fromisoformat(obj.timestamp)
        obj.timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        _format_response(
            obj=obj,
            title=title,
            header=header,
            highlight=obj.description,
        )

@transaction.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific transaction. '''
    service = client.financial_transactions.get

    if obj := _handle_response(service, resource_id=id):
        header = f'R$ {obj.amount}'
        title = f'{obj.account.name} {obj.type}'
        timestamp = datetime.fromisoformat(obj.timestamp)
        obj.timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        _format_response(
            obj=obj,
            title=title,
            header=header,
            highlight=obj.description,
        )

@transaction.command
@click.option('-l', '--limit', default=50)
@click.option('-p', '--page', default=0)
@click.option('-b', '--bank')
def all(limit: int, page: int, bank: str) -> None:
    ''' Retrieve all transactions. '''
    service = client.financial_transactions.all

    if response := _handle_response(service, limit=limit, page=page):
        results = response.results
        if bank:
            results = [
                obj for obj in results if obj.account.name == bank.title()
            ]
            click.echo(f'\nResults: {len(results)}')
        else:
            click.echo(f'\nResults: {response.count}')
            if limit < response.count:
                click.echo(
                    f'Showing: {len(response.results)} out of {response.count}'
                ) 
            if response.next:
                click.echo(f'For next page: --page <number>')

        for obj in results:
            header = f'R$ {obj.amount}'
            title = f'\n{obj.account.name} {obj.type}'
            remove = [
                'type',
                'description',
                'amount',
                'payment',
                'linked',
                'account',
                'operator',
            ]
            timestamp = datetime.fromisoformat(obj.timestamp)
            obj.timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            _format_response(
                obj=obj,
                title=title,
                header=header,
                highlight=obj.description,
                remove=remove,
            )

@transaction.command
@click.argument('ids', nargs=-1)
def delete(ids: str) -> None:
    ''' Delete an specific transaction. '''
    service = client.financial_transactions.delete

    while True:
        prompt = click.style('Proceed to deletion? [y/n] ', fg='red')
        confirmation = input(prompt)
        if confirmation == 'n':
            sys.exit(0)
        elif confirmation == 'y':
            break

    if len(ids) > 1:
        spinner()

    for id in ids:
        time.sleep(0.5)
        if obj := _handle_response(service, resource_id=id):
            _format_response(obj, 'DELETED', 'Done', color='red')

@transaction.command
@click.option('-s', '--search')
@click.option('-d', '--date')
@click.option('-sd', '--start-date')
@click.option('-ed', '--end-date')
@click.option('-b', '--bank')
@click.option('-l', '--limit', default=50)
@click.pass_context
def filter(
    ctx,
    search: str,
    date: str,
    start_date: str,
    end_date: str,
    bank: str,
    limit: int,
    ) -> None:
    ''' Filter transactions. '''
    if not any([search, date, start_date, end_date]):
        click.echo(ctx.get_help())
        sys.exit(0)

    service = client.financial_transactions.filter

    if response := _handle_response(
        service,
        search=search,
        date=date,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ):
        results = response.results
        if bank:
            results = [
                obj for obj in results if obj.account.name == bank.title()
            ]
            click.echo(f'\nResults: {len(results)}')
        else:
            click.echo(f'\nResults: {response.count}')
            if limit < response.count:
                click.echo(
                    f'Showing: {len(response.results)} out of {response.count}'
                ) 
            if response.next:
                click.echo(f'For next page: --page <number>')

        for obj in results:
            header = f'R$ {obj.amount}'
            title = f'\n{obj.account.name} {obj.type}'
            remove = [
                'type',
                'description',
                'amount',
                'payment',
                'linked',
                'account',
                'operator',
            ]
            timestamp = datetime.fromisoformat(obj.timestamp)
            obj.timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            _format_response(
                obj=obj,
                title=title,
                header=header,
                highlight=obj.description,
                remove=remove,
            )
