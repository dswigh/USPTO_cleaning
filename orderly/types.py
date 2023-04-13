import typing

# we ignore types below so that we dont have to go through the hassle of the protobuf stubs being installed
# import google.protobuf.pyext._message  # type: ignore
# from google.protobuf import message as _message

# IDENTIFIERS_MSG = _message.RepeatedCompositeContainer

# import ord_schema

IDENTIFIERS_MSG = typing.Any #ord_schema.proto.reaction_pb2.ReactionIdentifier

MOLECULE_IDENTIFIER = str
SMILES = str
CANON_SMILES = str  # This is for SMILES canonicalised by RDKit

RXN_STR = str

REAGENT = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_REAGENT = CANON_SMILES
REAGENTS = typing.List[REAGENT]
CANON_REAGENTS = typing.List[CANON_REAGENT]

REACTANT = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_REACTANT = CANON_SMILES
REACTANTS = typing.List[REACTANT]
CANON_REACTANTS = typing.List[CANON_REACTANT]

CATALYST = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_CATALYST = CANON_SMILES
CATALYSTS = typing.List[CATALYST]
CANON_CATALYSTS = typing.List[CANON_CATALYST]

PRODUCT = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_PRODUCT = CANON_SMILES
PRODUCTS = typing.List[PRODUCT]
CANON_PRODUCTS = typing.List[CANON_PRODUCT]

SOLVENT = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_SOLVENT = CANON_SMILES
SOLVENTS = typing.List[SOLVENT]
CANON_SOLVENTS = typing.List[CANON_SOLVENT]

METAL = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_METAL = CANON_SMILES
METALS = typing.List[METAL]
CANON_METALS = typing.List[CANON_METAL]

AGENT = typing.Union[CANON_SMILES, SMILES, MOLECULE_IDENTIFIER]
CANON_AGENT = CANON_SMILES
AGENTS = typing.List[AGENT]
CANON_AGENTS = typing.List[CANON_AGENT]

YIELD = float
YIELDS = typing.List[typing.Optional[YIELD]]

TEMPERATURE_CELCIUS = float
TEMPERATURES_CELCIUS = typing.List[typing.Optional[TEMPERATURE_CELCIUS]]

RXN_TIME = float  # hours
