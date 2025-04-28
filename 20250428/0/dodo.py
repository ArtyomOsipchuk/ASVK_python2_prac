from pathlib import Path


DOIT_CONFIG = {'default_tasks': ['docs']}

def task_docs():
    """Build docs with doit"""
    return {
        'file_dep': [*Path(".").glob("*.py"), *Path(".").glob("*.rst")],
        'actions': ['sphinx-build -M html source _build']
    }

def task_erase():
    """Erase smthg with doit"""
    return {
        'actions': ['git reset --hard', 'git clean -xdf']
    }
