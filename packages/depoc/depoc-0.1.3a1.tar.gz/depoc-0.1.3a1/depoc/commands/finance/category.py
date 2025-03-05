import depoc
import click
import sys
import time

from typing import Any

from ..utils._response import _handle_response
from ..utils._format import _format_response, spinner


client = depoc.DepocClient()


@click.group
def category() -> None:
    ''' Manage financial categories '''
    pass

@category.command
@click.argument('name')
@click.option('--parent', help='Inform the Parent Caregory if any.')
def create(name: str, parent: str) -> None:
    ''' Create a new category. '''
    data: dict[str, Any] = {'name': name}
    data.update({'parent': parent}) if parent else None

    service = client.financial_categories.create

    if obj := _handle_response(service, data):
        highlight = f'{obj.parent.name}' if obj.parent.name else ''
        _format_response(obj, obj.name, highlight)

@category.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific category '''
    service = client.financial_categories.get

    if obj := _handle_response(service, resource_id=id):
            highlight = f'{obj.parent.name}' if obj.parent.name else ''
            _format_response(obj, obj.name, highlight)

@category.command
@click.option('-l', '--limit', default=50)
@click.option('-p', '--page', default=0)
@click.option('--oneline', is_flag=True)
def all(limit: int, page: int, oneline: bool) -> None:
    ''' Retrieve all categories '''
    service = client.financial_categories.all

    if response := _handle_response(service, limit=limit, page=page):
        click.echo(f'\nResults: {response.count}')
        if limit < response.count:
            click.echo(
                f'Showing: {len(response.results)} out of {response.count}'
            ) 
        if response.next:
            click.echo(f'For next page: --page <number>')

        for obj in response.results:
            highlight = f'{obj.parent.name}' if obj.parent.name else ''
            remove = ['name', 'is_active', 'parent']

            if oneline:
                message = f'{obj.name.upper()}: {obj.id}'
                style = click.style(message, fg='yellow', bold=True)
                click.echo(style)
            else:
                _format_response(obj, obj.name, highlight, remove=remove)

@category.command
@click.argument('id')
@click.option('--name', help='Inform the new name for the Category.')
@click.option('--parent', help='Inform the Parent Caregory if any.')
@click.option('--activate', is_flag=True, help='Activate category.')
def update(id: str, name: str, parent: str, activate: bool) -> None:
    ''' Update a category '''
    data: dict[str, Any] = {}
    data.update({'name': name}) if name else None
    data.update({'parent': parent}) if parent else None
    data.update({'is_active': True}) if activate else None

    service = client.financial_categories.update

    if obj := _handle_response(service, data, id):
        highlight = f'{obj.parent.name}' if obj.parent.name else ''
        _format_response(obj, 'UPDATED', highlight, color='green')

@category.command
@click.argument('ids', nargs=-1)
def delete(ids: str) -> None:
    ''' Delete a category '''
    service = client.financial_categories.delete

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
