import click

from datafact.templates.items import fact_templates


@click.command('templates')
def templates_cli():
    """
    list available templates.
    """
    click.secho('Available templates:\n')

    for idx, temp in enumerate(fact_templates):
        click.secho('---')
        click.secho(f"{idx + 1:02}: {temp.name}", fg='green', bold=True)
        click.secho(temp.description)
        click.secho('')

    click.secho('--EOF--')
