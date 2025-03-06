
import sys

from besmarts.codecs import codec_rdkit 
from besmarts.codecs import codec_native

gcd = codec_rdkit.graph_codec_rdkit()

for fname in sys.argv[1:]:
    for g in codec_native.graph_codec_native_load(fname):
        print(gcd.smiles_encode(g))
