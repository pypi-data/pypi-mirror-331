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
        client = depoc.DepocClient()
        me = client.me.get()
        click.echo(f'Welcome {me.name}!')

        with open('token.json', 'w') as f:
            json.dump({'token': auth.token}, f)
            
    except APIError as e:
        click.echo(str(e.message))
