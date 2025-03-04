import click

from .commands import account
from .commands import login
from .commands import logout
from .commands import me
from .commands import finance
from .commands import contact
from .commands import receivable
from .commands import payable
from .commands import report

@click.group()
def main() -> None:
   pass
 
main.add_command(account)
main.add_command(login)
main.add_command(logout)
main.add_command(me)
main.add_command(finance.bank)
main.add_command(finance.category)
main.add_command(finance.transaction)
main.add_command(contact)
main.add_command(receivable)
main.add_command(payable)
main.add_command(report)
