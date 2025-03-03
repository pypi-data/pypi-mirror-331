from rdkit.Chem import rdFingerprintGenerator
from rdkit import Chem

MFPGEN = rdFingerprintGenerator.GetMorganGenerator(1)
ao = rdFingerprintGenerator.AdditionalOutput()
ao.AllocateBitInfoMap()
ao.AllocateAtomToBits()


def mol_to_pairs(mol):
    """
    Fractures each bond in the molecule and returns pairs of ECFP2 fingerprints
    (including dummy atoms) at the fracture points.
    """
    id_pairs = []
    for bond in mol.GetBonds():
        begin_atom_idx = bond.GetBeginAtomIdx()
        end_atom_idx = bond.GetEndAtomIdx()

        # create a new molecule by fragmenting the current bond
        new_mol = Chem.FragmentOnBonds(mol, [bond.GetIdx()])

        try:
            Chem.SanitizeMol(new_mol)
            # sparse fingerprints for the fractured atoms
            MFPGEN.GetSparseFingerprint(
                new_mol, fromAtoms=[begin_atom_idx, end_atom_idx], additionalOutput=ao
            )
            # extract the fingerprint IDs for the atoms
            fingerprint_ids = tuple(
                sorted(
                    [
                        ao.GetAtomToBits()[idx][1]
                        for idx in [begin_atom_idx, end_atom_idx]
                    ]
                )
            )
            id_pairs.append(fingerprint_ids)

        except Chem.rdchem.KekulizeException:
            pass
        except Exception as e:
            pass
    return id_pairs


def assess_per_bond(mol, profile):
    pairs = mol_to_pairs(mol)
    total = profile["setsize"]
    idx = profile["idx"]
    pair_counts = profile["pairs"]
    results = []
    for pair in pairs:
        o1 = idx.get(pair[0], 0) / total / 2
        o2 = idx.get(pair[1], 0) / total / 2
        expected = o1 * o2
        real = pair_counts.get(pair, 0) / total
        results.append(0 if expected == 0 else real / expected)
    return results


def score_mol(mol, profile, t):
    apb = assess_per_bond(mol, profile)
    if not apb:
        apb = [0]
    min_val = min(apb)
    info = {"bad_bonds": [i for i, b in enumerate(apb) if b < t]}
    score = min(0.5 * (min_val / t) ** 0.5, 1.0)
    return score, info
