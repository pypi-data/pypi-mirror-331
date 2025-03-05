import depoc
import click

from .utils._response import _handle_response


client = depoc.DepocClient()


@click.command
@click.option('-d', '--date', default='week')
@click.option('-sd', '--start-date')
@click.option('-ed', '--end-date')
@click.pass_context
def report(ctx, date: str, start_date: str, end_date: str) -> None:
    ''' Financial report for a specific period. '''
    division = f'{'':->50}'

    current_balance: float = 0
    total_receivable: float = 0
    total_payable: float = 0
    
    banks = client.financial_accounts.all
    receivables = client.receivables.filter
    payables = client.payables.filter

    if banks_response := _handle_response(banks):
        for obj in banks_response.results:
            current_balance += float(obj.balance)
        click.echo(division)
        format_current_balance = f'R$ {current_balance:.2f}'
        txt = f'BALANCE{format_current_balance:>43}'
        click.echo(txt)
        click.echo(division)

    if receivables_response := _handle_response(
        receivables,
        date=date,
        start_date=start_date,
        end_date=end_date,
    ):  
        for obj in receivables_response.results:
            total_receivable += float(obj.outstanding_balance)
        format_total_receivable = f'R$ {total_receivable:.2f}'
        txt = f'RECEIVABLE{format_total_receivable:>40}'
        click.echo(txt)
        click.echo(division)

    if payables_response := _handle_response(
        payables,
        date=date,
        start_date=start_date,
        end_date=end_date,
    ):
        for obj in payables_response.results:
            total_payable += float(obj.outstanding_balance)
        format_total_payable = f'R$ {total_payable:.2f}'
        txt = f'PAYABLE{format_total_payable:>43}'
        click.echo(txt)

        total_balance = round(
            current_balance + total_receivable - total_payable, 2
        )
        format_total_balance = f'R$ {total_balance:.2f}'
        color = 'red' if total_balance < 0 else 'green'

        click.echo(click.style(division, fg=color, bold=True))
        
        txt = click.style(
            f'RESULT{format_total_balance:>44}',
            fg=color,
            bold=True
        )
        click.echo(txt)

        click.echo(click.style(division, fg=color, bold=True))
