from pathlib import Path

required = [
    'app.py', 'README.md', 'INSTALL.md', 'LICENSE', 'requirements.txt',
    'pages', 'utils', 'docs', 'examples', 'config.yaml',
    'utils/data_engine.py', 'utils/file_parser.py', 'utils/aeb_model.py'
]
missing = [p for p in required if not Path(p).exists()]
if missing:
    print('Missing required files:', missing)
    raise SystemExit(1)
print('AEB selfcheck passed.')
