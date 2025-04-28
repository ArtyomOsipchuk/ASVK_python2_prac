from pathlib import Path
from zipfile import ZipFile


DOIT_CONFIG = {'default_tasks': ['docs']}
DOCZIP = 'docs.zip'
DOCLIST = 'docs.list'

def task_docs():
    """Build documentation"""
    return {
        'file_dep': [*Path(".").glob("*.py"), *Path(".").glob("*.rst")],
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
