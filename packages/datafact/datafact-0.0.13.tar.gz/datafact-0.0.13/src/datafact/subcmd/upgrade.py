import os
import sys

import click

from datafact.proj import load_config, ProjectConfig
from datafact.templates.items import template_mapping


@click.command('upgrade')
def upgrade_cli():
    """
    upgrade project.py to the latest version
    """
    if os.path.exists('project.py'):
        cfg = ProjectConfig.load_config()
        proj_py_template = template_mapping(
            ('datafact.templates.common', 'project.py.jinja2'),
            'project.py'
        )
        proj_py_template.render(
            './',
            cfg.get_render_context('./')
        )
        click.secho('done.', fg='green')
    else:
        click.secho('project.py not found.', fg='red')
        sys.exit(1)
