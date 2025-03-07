import os
import sys
from datetime import datetime

import click
from datafact.proj import locate_draft_file, load_config


# pragma: no cover
@click.group('experimental')
def experimental_cli():
    """
    experimental features.
    """
    pass


# pragma: no cover
@experimental_cli.command('auto-doc')
def auto_doc_cmd(): # pragma: no cover
    """
    initialize a dataset factory project.
    """
    cfg = load_config()
    dataset_name = cfg.name

    with open('./README.md') as f:
        old_readme = f.read()

    if os.path.exists('./type.py'):
        with open('./type.py') as f:
            type_doc = f.read()
    else:
        click.secho('type.py not found.', fg='red')
        sys.exit(1)

    comment = click.prompt('any comment about this dataset?', type=str, default='')

    try:
        from openai import OpenAI
        from mkb import def_fn
    except ImportError:
        click.secho('Please install openai and mkb first.', fg='red')
        sys.exit(1)

    mkb_openai_api_key = os.environ.get('MKB_OPENAI_API_KEY', None)

    if mkb_openai_api_key is None:
        open_ai_key_file = os.path.expanduser('~/.openai.key')
        if os.path.exists(open_ai_key_file):
            with open(open_ai_key_file) as f:
                mkb_openai_api_key = f.read().strip()

    if mkb_openai_api_key is None or mkb_openai_api_key == '':
        click.secho('Please set MKB_OPENAI_API_KEY environment variable or ~/.openai.key file.', fg='red')
        sys.exit(1)

    from mkb.impl.openai import GptApiOptions
    openai_client = OpenAI(api_key=mkb_openai_api_key)

    my_gpt_opts = GptApiOptions(temperature=1.0)

    @def_fn.openai(client=openai_client, opts=my_gpt_opts)
    @def_fn.with_instruction(
        "Given a dataset_name, data type definition and a comment about the dataset, "
        "write a readme document for the dataset."
        "do not show type doc in readme and write about the overview, attributes, description and potential use case for this dataset."
    )
    @def_fn.with_example(
        input={
            'dataset_name': 'geo/country',
            'data_type': """```
from easytype import TypeBuilder
from dataset_sh.constants import DEFAULT_COLLECTION_NAME

CountryCodeInfo = TypeBuilder.create(
    'CountryCodeInfo',
    code=str,
    name=str,
    native=str,
)

data_types = {
    DEFAULT_COLLECTION_NAME: CountryCodeInfo
}
```
""",
            'comment': 'a dataset about iso-639 country code.'
        },
        output="""
This dataset contains **ISO 639-1**: The International Standard for country codes and codes for their subdivisions.

This dataset provides information on languages, including:

- **ISO Language Code** (`code`): A unique, two-letter code representing the language, following the ISO 639-1 standard.
- **Language Name in English** (`name`): The name of the language in English.
- **Native Name** (`native`): The name of the language as written in its native script or language form.        
        """.strip()
    )
    def write_dataset_readme(dataset_name, data_type, comment=''):
        # any code you wrote here will be ignored.
        pass

    readme = write_dataset_readme(
        dataset_name=dataset_name,
        data_type=type_doc,
        comment=''
    )

    with open('./README.md') as f:
        old_readme = f.read()

    datetime_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    with open(f'./README_{datetime_str}.md.backup', 'w') as f:
        f.write(old_readme)

    with open(f'./README.md', 'w') as f:
        f.write(readme.value)

    click.echo_via_pager('New readme generated:\n' + readme.value)
