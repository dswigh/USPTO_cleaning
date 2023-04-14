from typing import List, Dict, Set
from rdkit import Chem

import orderly.data.solvents

from orderly.types import *


def is_transition_metal(atom: Chem.Atom) -> bool:
    """Determines if an atom is a transition metal.
    Args:
        atom: The atom in question. Should be of type rdkit.Chem.rdchem.Atom
    Returns:
        Boolean for whether the atom is a transition metal.
    """
    atom_n = atom.GetAtomicNum()
    return bool((22 <= atom_n <= 29) or (40 <= atom_n <= 47) or (72 <= atom_n <= 79))


def has_transition_metal(smiles: SMILES) -> bool:
    """
    Determines if a molecule contains a transition metal.
    Args:
        mol: The molecule in question. Should be of type rdkit.Chem.rdchem.Mol
    Returns:
        Boolean for whether the molecule has a transition metal.

    Inspiration: https://github.com/open-reaction-database/ord-schema/blob/e114eb6360badbf3a2d0552bea20be0d438966a3/ord_schema/message_helpers.py?fbclid=IwAR0qQuhveV_YF98qrNXMf3njPmkHmzlkuUAYIGAFhEkc_1UnVZITZG4U8sU#L579
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False

    for atom in mol.GetAtoms():
        if is_transition_metal(atom):
            return True
    return False


def get_molecule_replacements() -> Dict[MOLECULE_IDENTIFIER, SMILES]:
    """
    Returns a dictionary mapping common representations of molecules (particularly catalysts) to a canonical representation.
    """
    molecule_replacements: Dict[str, str] = {}

    # Add a catalyst to the molecule_replacements dict (Done by Alexander)
    molecule_replacements[
        "CC(=O)[O-].CC(=O)[O-].CC(=O)[O-].CC(=O)[O-].[Rh+3].[Rh+3]"
    ] = "CC(=O)[O-].[Rh+2]"
    molecule_replacements[
        "[CC(=O)[O-].CC(=O)[O-].CC(=O)[O-].[Rh+3]]"
    ] = "CC(=O)[O-].[Rh+2]"
    molecule_replacements[
        "[CC(C)(C)[P]([Pd][P](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C]"
    ] = "CC(C)(C)[PH]([Pd][PH](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C"
    molecule_replacements[
        "CCCC[N+](CCCC)(CCCC)CCCC.CCCC[N+](CCCC)(CCCC)CCCC.CCCC[N+](CCCC)(CCCC)CCCC.[Br-].[Br-].[Br-]"
    ] = "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]"
    molecule_replacements["[CCO.CCO.CCO.CCO.[Ti]]"] = "CCO[Ti](OCC)(OCC)OCC"
    molecule_replacements[
        "[CC[O-].CC[O-].CC[O-].CC[O-].[Ti+4]]"
    ] = "CCO[Ti](OCC)(OCC)OCC"
    molecule_replacements[
        "[Cl[Ni]Cl.c1ccc(P(CCCP(c2ccccc2)c2ccccc2)c2ccccc2)cc1]"
    ] = "Cl[Ni]1(Cl)[P](c2ccccc2)(c2ccccc2)CCC[P]1(c1ccccc1)c1ccccc1"
    molecule_replacements[
        "[Cl[Pd](Cl)([P](c1ccccc1)(c1ccccc1)c1ccccc1)[P](c1ccccc1)(c1ccccc1)c1ccccc1]"
    ] = "Cl[Pd](Cl)([PH](c1ccccc1)(c1ccccc1)c1ccccc1)[PH](c1ccccc1)(c1ccccc1)c1ccccc1"
    molecule_replacements["[Cl[Pd+2](Cl)(Cl)Cl.[Na+].[Na+]]"] = "Cl[Pd]Cl"
    molecule_replacements["Cl[Pd+2](Cl)(Cl)Cl"] = "Cl[Pd]Cl"
    molecule_replacements["Karstedt catalyst"] = "C[Si](C)(C=C)O[Si](C)(C)C=C.[Pt]"
    molecule_replacements["Karstedt's catalyst"] = "C[Si](C)(C=C)O[Si](C)(C)C=C.[Pt]"
    molecule_replacements["[O=C([O-])[O-].[Ag+2]]"] = "O=C([O-])[O-].[Ag+]"
    molecule_replacements["[O=S(=O)([O-])[O-].[Ag+2]]"] = "O=S(=O)([O-])[O-].[Ag+]"
    molecule_replacements["[O=[Ag-]]"] = "O=[Ag]"
    molecule_replacements["[O=[Cu-]]"] = "O=[Cu]"
    molecule_replacements["[Pd on-carbon]"] = "[C].[Pd]"
    molecule_replacements["[TEA]"] = "OCCN(CCO)CCO"
    molecule_replacements["[Ti-superoxide]"] = "O=[O-].[Ti]"
    molecule_replacements[
        "[[Pd].c1ccc(P(c2ccccc2)c2ccccc2)cc1]"
    ] = "[Pd].c1ccc(P(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "[c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd-4]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1]"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "[c1ccc([P]([Pd][P](c2ccccc2)(c2ccccc2)c2ccccc2)(c2ccccc2)c2ccccc2)cc1]"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "[c1ccc([P](c2ccccc2)(c2ccccc2)[Pd]([P](c2ccccc2)(c2ccccc2)c2ccccc2)([P](c2ccccc2)(c2ccccc2)c2ccccc2)[P](c2ccccc2)(c2ccccc2)c2ccccc2)cc1]"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements["[sulfated tin oxide]"] = "O=S(O[Sn])(O[Sn])O[Sn]"
    molecule_replacements[
        "[tereakis(triphenylphosphine)palladium(0)]"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakistriphenylphosphine palladium"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "Pd(Ph3)4"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakistriphenylphosphine palladium(0)"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakistriphenylphosphine palladium (0)"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakis-(triphenylphosphine)palladium"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "Pd[PPh3]4"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakis (triphenylphosphine)palladium(0)"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"
    molecule_replacements[
        "tetrakis triphenylphosphine palladium"
    ] = "c1ccc([PH](c2ccccc2)(c2ccccc2)[Pd]([PH](c2ccccc2)(c2ccccc2)c2ccccc2)([PH](c2ccccc2)(c2ccccc2)c2ccccc2)[PH](c2ccccc2)(c2ccccc2)c2ccccc2)cc1"

    molecule_replacements["[zeolite]"] = "O=[Al]O[Al]=O.O=[Si]=O"

    # Molecules found among the most common names in molecule_names
    molecule_replacements["TEA"] = "OCCN(CCO)CCO"
    molecule_replacements["hexanes"] = "CCCCCC"
    molecule_replacements["Hexanes"] = "CCCCCC"
    molecule_replacements["hexanes ethyl acetate"] = "CCCCCC.CCOC(=O)C"
    molecule_replacements["EtOAc hexanes"] = "CCCCCC.CCOC(=O)C"
    molecule_replacements["EtOAc-hexanes"] = "CCCCCC.CCOC(=O)C"
    molecule_replacements["ethyl acetate hexanes"] = "CCCCCC.CCOC(=O)C"
    molecule_replacements["cuprous iodide"] = "[Cu]I"
    molecule_replacements["N,N-dimethylaminopyridine"] = "n1ccc(N(C)C)cc1"
    molecule_replacements["dimethyl acetal"] = "CN(C)C(OC)OC"
    molecule_replacements["cuprous chloride"] = "Cl[Cu]"
    molecule_replacements["N,N'-carbonyldiimidazole"] = "O=C(n1cncc1)n2ccnc2"
    molecule_replacements["CrO3"] = "O=[Cr](=O)=O"
    # SiO2
    # Went down the list of molecule_names until frequency was 806

    # Alternative replacements. These words may be more ambiguous than the replacements above. (e.g. does 'ice' mean icebath or ice in the reaction?)
    molecule_replacements["aqueous solution"] = "O"
    molecule_replacements["ice water"] = "O"
    molecule_replacements["water"] = "O"
    molecule_replacements["ice"] = "O"
    return molecule_replacements


def get_molecule_str_force_nones() -> List[INVALID_IDENTIFIER]:
    return [
        "solution",  # someone probably wrote 'water solution' and that was translated to 'water' and 'solution' I'd imagine
        "liquid",
    ]


def get_solvents_set() -> Set[SOLVENT]:
    return orderly.data.solvents.get_solvents_set()
