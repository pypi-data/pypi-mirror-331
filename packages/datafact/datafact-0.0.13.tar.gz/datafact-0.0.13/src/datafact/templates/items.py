import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, TypedDict, Optional

import jinja2
from importlib import resources


class Context(TypedDict):
    name: str


@dataclass
class FilenameMapping:
    source: tuple[str, str]
    target: Optional[str] = None
    target_fn: Optional[Callable[[Context], str]] = None

    def render(self, project_folder, context):
        if self.target_fn:
            target_file = self.target_fn(context)
        else:
            target_file = self.target

        template_package, template_name = self.source
        rendered = render_template(template_package, template_name, context)
        out_file = f'{project_folder}/{target_file}'
        if os.path.exists(out_file):
            shutil.copy(out_file, out_file + f'.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}')
        with open(out_file, 'w') as f:
            f.write(rendered)


def render_template(template_package, template_name, context):
    # Load the template from the package's resources
    with resources.open_text(template_package, template_name) as template_file:
        template = jinja2.Template(template_file.read())
    return template.render(context)


def template_mapping(source, target_str_or_fn):
    if isinstance(target_str_or_fn, str):
        return FilenameMapping(source=source, target=target_str_or_fn)
    elif callable(target_str_or_fn):
        return FilenameMapping(source=source, target_fn=target_str_or_fn)
    else:
        raise ValueError("target_str_or_fn must be either a string or a callable")


@dataclass
class DataFactProjectHelpMessage:
    message: str
    kwargs: dict = field(default_factory=dict)


@dataclass
class DataFactProjectTemplate:
    name: str
    description: str
    files: list[FilenameMapping] = field(default_factory=list)
    message: list[DataFactProjectHelpMessage] = field(default_factory=list)

    def create(self, project_folder, context):
        for file in self.files:
            file.render(project_folder, context)


crawler_template = DataFactProjectTemplate(
    name='crawler',
    description='Build dataset by crawling a website.',
    files=[
        template_mapping(('datafact.templates.common', 'project.py.jinja2'), 'project.py'),
        template_mapping(('datafact.templates.common', 'gitignore.jinja2'), '.gitignore'),
        template_mapping(('datafact.templates.common', 'README.md.jinja2'), 'README.md'),
    ],
    message=[
        DataFactProjectHelpMessage(
            message='To run the project, run the following command: python project.py',
        )
    ]
)

mkb_template = DataFactProjectTemplate(
    name='synthetic',
    description='Build dataset using synthetic data.',
    files=[
        template_mapping(('datafact.templates.common', 'project.py.jinja2'), 'project.py'),
        template_mapping(('datafact.templates.common', 'gitignore.jinja2'), '.gitignore'),

        template_mapping(('datafact.templates.synthetic', 'README.md.jinja2'), 'README.md'),
        template_mapping(('datafact.templates.synthetic', 'data.py.jinja2'), 'data.py'),
        template_mapping(('datafact.templates.synthetic', 'type.py.jinja2'), 'type.py'),
        template_mapping(('datafact.templates.synthetic', 'fn.py.jinja2'), 'fn.py'),

    ],
    message=[
        DataFactProjectHelpMessage(
            message='To run the project, run the following command: python project.py',
        )
    ]
)

hello_world_template = DataFactProjectTemplate(
    name='hello-world',
    description='A simple hello world project',
    files=[
        template_mapping(('datafact.templates.common', 'project.py.jinja2'), 'project.py'),
        template_mapping(('datafact.templates.common', 'gitignore.jinja2'), '.gitignore'),

        template_mapping(('datafact.templates.helloworld', 'README.md.jinja2'), 'README.md'),
        template_mapping(('datafact.templates.helloworld', 'data.py.jinja2'), 'data.py'),
        template_mapping(('datafact.templates.helloworld', 'type.py.jinja2'), 'type.py'),
    ],
    message=[
        DataFactProjectHelpMessage(
            message='see README.md for more information.',
        )
    ]
)

media_template = DataFactProjectTemplate(
    name='media',
    description='create dataset with media files',
    files=[
        template_mapping(('datafact.templates.common', 'project.py.jinja2'), 'project.py'),
        template_mapping(('datafact.templates.common', 'gitignore.jinja2'), '.gitignore'),

        template_mapping(('datafact.templates.common', 'bin_files_true.py.jinja2'), 'bin_files.py'),

        template_mapping(('datafact.templates.media', 'README.md.jinja2'), 'README.md'),
        template_mapping(('datafact.templates.media', 'data.py.jinja2'), 'data.py'),
        template_mapping(('datafact.templates.media', 'type.py.jinja2'), 'type.py'),
    ],
    message=[
        DataFactProjectHelpMessage(
            message='see README.md for more information.',
        )
    ]
)

fact_templates = [
    hello_world_template,
    mkb_template,
    media_template
]
