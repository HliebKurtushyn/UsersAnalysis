# Data-Driven Banking Platform

Навчальний full-stack проєкт на Flask, SQLite та Python.

## Запуск

```bash
pip install -r requirements.txt
python run.py
```

Тести запускаються командою:

```bash
pytest
```

## Pre-commit

Встановити залежності та активувати git hooks:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Перевірити всі файли вручну:

```bash
pre-commit run --all-files
```

Перед кожним комітом hooks автоматично перевіряють форматування, базову коректність файлів і запускають тести.
