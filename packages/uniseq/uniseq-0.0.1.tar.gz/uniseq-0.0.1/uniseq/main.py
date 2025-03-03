import requests
from io import StringIO
from Bio import SeqIO

def getseq(identifier):
    """
    Fetches the protein sequence from the UniProtKB database using its REST API.

    The sequence is retrieved in FASTA format and parsed using Biopython 
    to extract the sequence information.

    Parameters
    ----------
    identifier : str
        The UniProtKB identifier of the protein.

    Returns
    -------
    str
        The extracted protein sequence, which can be stored and used later.
    """
    
    record = requests.get(f'https://rest.uniprot.org/uniprotkb/{identifier}.fasta')

    # check to ensure a successful request
    if record.status_code != 200:
        raise ValueError(f"Failed to fetch data for {identifier}. HTTP Status: {record.status_code}")

    # parsing of web scraped text
    fasta_io = StringIO(record.text)
    
    # retrieval of sequence from fasta using biopython functionality
    for r in SeqIO.parse(fasta_io, 'fasta'):
        return str(r.seq)  

    return None

