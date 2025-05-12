from pathlib import Path
from zipfile import ZipFile


DOIT_CONFIG = {'default_tasks': ['docs']}
DOCZIP = 'docs.zip'
DOCLIST = 'docs.list'

def task_wheel():
    return {
        'actions': ['python3 -m build --wheel'],
    }

def task_sdist():
    return {
        'actions': ['python3 -m build --sdist'],
    }

def task_docs():
    """Build documentation"""
    for form in ['rst', 'txt']:
        yield {
            'name': form,
            'file_dep': [*Path(".").glob("*.py"), *Path(".").glob(f"*.{form}")],
            'actions': ['sphinx-build -M html source _build']
        }

def task_erase():
    """Erase generates and new files"""
    return {
        'actions': ['git reset --hard', 'git clean -xdf']
    }

def task_zip():
    """Zip builded html to docs.zip"""
    return {
        'actions': [f'zip -r {DOCZIP} _build/html']
    }

def zipper(outfile, infile):
    """convert zip names to .list"""
    with ZipFile(outfile) as outzip:
        names = outzip.namelist()
    with open(infile, "w") as inzip:
        print("\n".join(names), file=inzip)

def task_stat():
    """Archive documentation"""
    return {
        'actions': [(zipper, [f'{DOCZIP}', f'{DOCLIST}'])],
        'file_dep': [f'{DOCZIP}'],
        'targets': [f'{DOCLIST}']
    }
