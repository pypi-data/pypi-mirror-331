import depoc
import json
import click
        

@click.command(help='Logout of your account')
def logout() -> None:
    with open(depoc.token_path, 'w') as f:
        json.dump({'token': None}, f)
