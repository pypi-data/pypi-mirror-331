"""
besmarts.decode_rdkit
"""

import sys

from besmarts.codecs import codec_rdkit 
from besmarts.core import graphs


gcd = codec_rdkit.graph_codec_rdkit()

for smi in sys.argv[1:]:
    G = gcd.smiles_decode(smi)
    print("\n".join(codec_native.graph_save(G)))


