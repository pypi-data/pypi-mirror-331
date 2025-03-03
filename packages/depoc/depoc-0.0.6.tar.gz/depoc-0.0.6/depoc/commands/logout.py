import json
import click
        

@click.command(help='Logout of your account')
def logout() -> None:
    with open('token.json', 'w') as f:
        json.dump({'token': None}, f)
