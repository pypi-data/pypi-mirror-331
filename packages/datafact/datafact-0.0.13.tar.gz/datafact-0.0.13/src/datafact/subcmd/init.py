import os
import sys

import click
from dataset_sh.utils.misc import count_slashes, is_name_legit

from datafact.proj import CONFIG_FILENAME, ProjectConfig
from datafact.templates.items import fact_templates


@click.command('new')
@click.option('--template', '-t',
              type=str,
              default='hello-world',
              help='choose a project template')
@click.option(
    '--dir', '-d', 'project_dir',
    default=None,
    help='directory to create the project in.'
)
@click.option(
    '--ignore-user-dir', '-i', 'ignore_user_dir',
    is_flag=True,
    default=False,
    help='ignore user directory'
)
@click.argument('name',
                type=str)
def init_cli(
        template,
        project_dir,
        ignore_user_dir,
        name
):
    """
    initialize a dataset factory project.
    """
    selected_template = None
    for t in fact_templates:
        if t.name == template:
            selected_template = t

    if not selected_template:
        click.secho(f'Template {template} not found.', err=True, fg='red')
        sys.exit(1)

    if name is None:
        current_folder_name = os.path.basename(os.getcwd())
        name = click.prompt(f'Enter dataset name', type=str, default=f'local/{current_folder_name}')

    if name:
        if '/' not in name:
            name = f'local/{name}'

        if count_slashes(name) == 1:
            username, dataset_name = name.split('/')
            if is_name_legit(username) and is_name_legit(dataset_name):
                pass

                if project_dir is None:

                    if ignore_user_dir:
                        suggested_project_dir = os.path.join('./', dataset_name)
                    else:
                        suggested_project_dir = os.path.join('./', username, dataset_name)

                    project_dir = click.prompt(f'where to create this project', type=str, default=suggested_project_dir)

                cfg_file_path = os.path.join(project_dir, CONFIG_FILENAME)
                if os.path.exists(cfg_file_path):
                    click.echo(f'Config file {cfg_file_path} already exists.', err=True)
                    sys.exit(1)

                os.makedirs(project_dir, exist_ok=True)
                ProjectConfig.init_config(name, base_folder=project_dir)
                selected_template.create(project_dir, {
                    'username': username,
                    'dataset_name': dataset_name,
                    'name': name,
                    'project_dir': project_dir
                })
                click.secho('Project created successfully.', fg='green')
                readme_path = os.path.join(project_dir, 'README.md')
                if os.path.exists(readme_path):
                    with open(readme_path) as f:
                        click.secho(f.read(), fg='yellow')
            else:
                click.secho('Invalid dataset name.', fg='red')
                sys.exit(1)

        else:
            click.secho('Project name must in the format of username/dataset_name or dataset_name.', fg='red')
            sys.exit(1)
    else:
        click.echo('Name is missing.', err=True)
        sys.exit(1)
