import click

from typing import Literal

from depoc.objects.base import DepocObject


def _format_response(
        obj: DepocObject,
        title: str,
        header: str,
        highlight: str | None = None,
        color: Literal[
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
        ] = 'yellow',
        remove: list[str] | None = None,
    ):
    
    try:
        if obj.is_active == False:
            color = 'red'
    except AttributeError:
        pass

    title = click.style(f'{title.upper():-<51}', fg=color, bold=True)
    division = click.style(f'\n{'':->50}', fg=color, bold=True)
    header = click.style(f'\n{header:>50}', bold=True)
    space = '\n'

    if highlight:
        highlight = click.style(f'\n{highlight:>50}', bold=True)

    data = obj.to_dict()
    body: str = ''

    if remove:
        for item in remove:
            data.pop(item)

    for k, v in data.items():
        k = k.replace('_', ' ').title()
        k = k.upper() if k == 'Id' else k

        if isinstance(v, DepocObject):
            if hasattr(v, 'name'):
                v = v.name

        body += f'\n{k}: {v}'

    response = (
        f'{title}'
        f'{header}'
        f'{highlight if highlight else ''}'
        f'{space}'
        f'{body}'
        f'{division}'
    )
    click.echo(response)
