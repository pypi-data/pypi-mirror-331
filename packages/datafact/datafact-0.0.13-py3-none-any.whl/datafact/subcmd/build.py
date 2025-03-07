import os
import sys
from importlib.metadata import version

import click
from dataset_sh import create
from dataset_sh.utils.dump import dump_collections
from dataset_sh.utils.misc import get_tqdm
from tqdm import tqdm

from datafact.proj import locate_draft_file


def get_build_command(create_data_dict, data_types, media_files_fn=None):
    def build_dataset(dist_name, description=None, overwrite=None):
        click.secho(f"You are building with dataset.sh version: {version('dataset_sh')}\n", fg='yellow')
        fp = locate_draft_file(dist_name)

        if os.path.exists(fp):
            if not overwrite:
                click.secho(f'dataset.sh file already exists at {fp}, use --overwrite/-o to overwrite.', fg='red')
                sys.exit(1)
            else:
                click.secho(f'removing existing file at {fp}')

        click.secho(f'creating dataset.sh file at {fp}')

        data_dict = create_data_dict()

        if media_files_fn is None:
            dump_collections(
                fp,
                data_dict,
                type_dict=data_types,
                description=description,
            )
        else:
            type_dict = data_types
            inner_tqdm = get_tqdm()
            with create(fp) as out:
                if description:
                    out.meta.description = description
                for name, data in data_dict.items():
                    print(f'Importing collection {name}')
                    if len(data) > 0:
                        type_annotation = type_dict.get(name, None)
                        out.add_collection(name, data, type_annotation=type_annotation, tqdm=inner_tqdm)
                print('Importing media files')
                for name, content in tqdm(media_files_fn()):
                    out.add_binary_file(name, content)

        click.secho('done.\n', fg='green')

        click.secho('Hint:\npreview your dataset with the following command:', fg='yellow')
        click.secho('python project.py preview show\n', fg='yellow', bold=True)

        click.secho('publish your dataset with the following command:', fg='yellow')
        click.secho('python project.py publish\n', fg='yellow', bold=True)

    @click.command(name='build')
    @click.option('--name', '-n', type=str, default='draft', help='draft dataset.sh file name.')
    @click.option('--message', '-m', type=str, default='', help='short commit message for this dataset version.')
    @click.option('--overwrite', '-o', is_flag=True, help='overwrite existing dataset.sh file.')
    def build_cli(name, message, overwrite):
        """
        build dataset draft.
        """
        build_dataset(name, message, overwrite)

    return build_cli
