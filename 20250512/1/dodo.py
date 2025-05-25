from pathlib import Path
from zipfile import ZipFile
from doit.tools import create_folder
from shutil import rmtree

PODEST = 'mood/locales'
DOIT_CONFIG = {'default_tasks': ['html']}
DOCZIP = 'docs.zip'
DOCLIST = 'docs.list'

def task_wheel():
    """Create build with wheel."""
    return {
        'actions': ['python3 -m build --wheel'],
    }

def task_sdist():
    """Create build with sdist."""
    return {
        'actions': ['python3 -m build --sdist'],
    }

def task_docs():
    """Build documentation."""
    for form in ['rst', 'txt']:
        yield {
            'name': form,
            'file_dep': [*Path(".").glob("*.py"), *Path(".").glob(f"*.{form}")],
            'actions': ['sphinx-build -M html source _build']
        }

def task_html():
    """Build html ducs."""
    return {
            'actions': ['sphinx-build -M html source mood/docs'],
           }

def task_pot():
    """Re-create .pot ."""
    return {
            'actions': [f'pybabel extract -o MUD.pot {PODEST}'],
            'file_dep': [*Path(".").glob("*.py")],
            'targets': ['MUD.pot'],
           }

def task_po():
    """Update translations."""
    return {
            'actions': [f'pybabel update -D MUD -d {PODEST} -l ru_RU.UTF-8 -i MUD.pot'],
            'file_dep': ['MUD.pot'],
            'targets': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MUD.po'],
           }

def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (create_folder, [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES']),
                f'pybabel compile -D MUD -l ru_RU.UTF-8 -d {PODEST}'
                       ],
            'file_dep': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MUD.po'],
            'targets': [f'{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MUD.mo'],
           }

def task_i18n():
    """Internalization Meta-task."""
    return {
            'actions': None,
            'task_dep': ['pot', 'po', 'mo'],
    }

def task_test():
    """Perform tests."""
    return {
            'actions': ['python3 -m mood.tests.ServerTest -v', 'python3 -m mood.tests.ClientTest -v'],
            'task_dep': ['i18n']
    }

def task_clean_targets():
    """Gitclean."""
    return {
            'actions': ['gir clean -xdf', 'rmtree docs']
    }

def task_erase():
    """Erase generates and new files."""
    return {
        'actions': ['git reset --hard', 'git clean -xdf']
    }

def task_zip():
    """Zip builded html to docs.zip ."""
    return {
        'actions': [f'zip -r {DOCZIP} _build/html']
    }

def zipper(outfile, infile):
    """convert zip names to .list ."""
    with ZipFile(outfile) as outzip:
        names = outzip.namelist()
    with open(infile, "w") as inzip:
        print("\n".join(names), file=inzip)

def task_stat():
    """Archive documentation."""
    return {
        'actions': [(zipper, [f'{DOCZIP}', f'{DOCLIST}'])],
        'file_dep': [f'{DOCZIP}'],
        'targets': [f'{DOCLIST}']
    }
