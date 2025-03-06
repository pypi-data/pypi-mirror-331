"""
Example using RDKit to decode a SMILES string and save to a native BESMARTS format.
"""

import sys

from besmarts.codecs import codec_rdkit 
from besmarts.codecs import codec_native

gcd = codec_rdkit.graph_codec_rdkit()

for smi in sys.argv[1:]:
    G = gcd.smiles_decode(smi)
    print("\n".join(codec_native.graph_save(G)))
