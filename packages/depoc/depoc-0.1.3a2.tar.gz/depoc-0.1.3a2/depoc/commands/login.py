import json
import depoc
import click

from depoc.utils._error import APIError


@click.command()
@click.option('--username', prompt=True, required=True)
@click.password_option(required=True, confirmation_prompt=False)
def login(username: str, password: str) -> None :
    ''' Enter in your account '''
    auth = depoc.Connection(username, password)
    
    try:
        depoc.token = auth.token
        click.echo(f'Welcome!')

        with open(depoc.token_path, 'w') as f:
            json.dump({'token': auth.token}, f)
            
    except APIError as e:
        click.echo(str(e.message))
