# Uniseq

**UniSeq** is a Python package that allows you to fetch protein sequences directly from the UniProtKB database using its REST API. This package can help in automating workflows that dynamically scrapes protein sequences from the database. 

## Installation
```bash
pip install uniseq
```

## Usage
```python
from uniseq import getseq

sequence = getseq("P69905")  # any valid UniProtKB ID can be passed
print(sequence)
```

## Dependencies
- requests
- biopython

These are automatically installed when you install the package.

