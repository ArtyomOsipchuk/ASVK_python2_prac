def task_docs():
    """Build docs with doit"""
    return {
        'actions': ['sphinx-build -M html source _build']
    }
