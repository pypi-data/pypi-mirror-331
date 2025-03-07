import os
import sys

import click

import dataset_sh as dsh

from datafact.proj import DEFAULT_TARGET, DatasetLocalTarget, load_config, locate_draft_file


def load_readme():
    readme_path = './README.md'
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            return f.read()
    return None


def publish_local(source, target: DatasetLocalTarget, tags: list[str]):
    dataset = dsh.dataset(target['name'])
    dataset.import_file(
        source,
        tags=tags
    )
    readme = load_readme()
    if readme:
        dataset.set_readme(readme)


@click.command(name='publish')
@click.option('--source', '-s',
              default='draft', type=str,
              help="source dataset draft name.")
@click.option('--target', '-t',
              default=DEFAULT_TARGET, type=str,
              help="publishing target name.")
@click.option('--tag',
              multiple=True,
              help="List of tags. e.g., --tag tag1 --tag tag2.")
def publish_cli(source, target, tag):
    """
    publish dataset draft to target.
    """
    cfg = load_config()
    t = cfg.get_target(target)

    tags = list(tag)

    if t is None:
        click.secho(f'Target {target} not found.', fg='red')
        sys.exit(1)

    source_file = locate_draft_file(source)

    if not os.path.exists(source_file):
        click.secho(f'Draft dataset file {source_file} not found.', fg='red')
        sys.exit(1)

    if t['type'] == 'local':
        publish_local(source_file, t, tags)
        click.secho(f'done.\n', fg='green')
        click.secho("Hint: use the following command to view the published dataset:\n")
        click.secho(f"dataset.sh gui {t['name']}\n", fg='cyan')
        click.secho("Publish to remote using the following command:\n")
        click.secho(f"dataset.sh remote -p default upload -s {t['name']} -t latest {t['name']} \n", fg='cyan')
    else:
        click.secho(f'Unknown target type: {t["type"]}', fg='red')
        sys.exit(1)
