"""
tests/test_torsion_angles.py
"""

from besmarts.codecs import codec_native
from besmarts.core import graphs
from besmarts.core import assignments


def run():

    global propane
    # load the default native graph codec. It can encode SMARTS/SMILES
    codecs = codec_native.primitive_codecs_get()
    atom_primitives = list(codec_native.primitive_codecs_get_atom())
    bond_primitives = list(codec_native.primitive_codecs_get_bond())
    gcd = codec_native.graph_codec_native(
        codecs,
        atom_primitives,
        bond_primitives
    )

    propane = [x.split() for x in propane.split('\n')]

    # load in a pre-decoded propane graph
    g = codec_native.graph_load(propane)
    smi = gcd.smiles_encode(g)

    _, xyzs = assignments.parse_xyz(xyzdata)

    sel = {}
    for ic, xyz in enumerate(xyzs[0], 1):
        if (ic,) not in sel:
            sel[ic,] = []
        sel[ic,].extend(xyz)

    pos = assignments.graph_assignment(smi, sel, g)

    ics = graphs.graph_torsions(g)

    ics_r = [ic[::-1] for ic in ics]

    t = assignments.graph_assignment_geometry_torsions(pos, indices=ics).selections
    tr = assignments.graph_assignment_geometry_torsions(pos, indices=ics_r).selections
    for (ic, a),  (ic_r, b) in zip(t.items(), tr.items()):
        print(ic, ic_r, a, b)


propane = """#GRAPH
#ATOM element hydrogen connectivity_total connectivity_ring ring_smallest aromatic formal_charge
#BOND bond_ring bond_order
  1   1  64   8  16   1   1   1   1
  2   2  64   4  16   1   1   1   1
  3   3  64   8  16   1   1   1   1
  4   4   2   1   2   1   1   1   1
  5   5   2   1   2   1   1   1   1
  6   6   2   1   2   1   1   1   1
  7   7   2   1   2   1   1   1   1
  8   8   2   1   2   1   1   1   1
  9   9   2   1   2   1   1   1   1
 10  10   2   1   2   1   1   1   1
 11  11   2   1   2   1   1   1   1
  1   2   1   2
  1   4   1   2
  1   5   1   2
  1   6   1   2
  2   3   1   2
  2   7   1   2
  2   8   1   2
  3   9   1   2
  3  10   1   2
  3  11   1   2"""

xyzdata = """11

C          1.06874       -0.04704       -0.01741
C          2.58793       -0.07492       -0.01197
C          3.12057       -1.47175        0.25790
H          0.70828        0.96760       -0.21342
H          0.66732       -0.36966        0.94863
H          0.66727       -0.70634       -0.79361
H          2.96290        0.61328        0.75365
H          2.96267        0.27816       -0.97919
H          2.78271       -1.83882        1.23238
H          4.21502       -1.46745        0.25712
H          2.78279       -2.17528       -0.50983"""

if __name__ == "__main__":
    run()
