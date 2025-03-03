# uniSeq

**UniSeq** is a Python package that allows you to fetch protein sequences directly from the UniProtKB database using its REST API.

## installation
```bash
pip install uniseq
```

## usage
```python
from uniseq import getseq

sequence = getseq("P69905")  # Example UniProt ID for Hemoglobin subunit alpha
print(sequence)
```

## dependencies
- requests
- biopython

These are automatically installed when you install the package.

