import typing

REPEATEDCOMPOSITECONTAINER = typing.TypeVar(
    "REPEATEDCOMPOSITECONTAINER", bound=typing.Iterable[typing.Any]
)  # protobuf uses a different type for the repeat composite container for each OS so we need a generic type that is not using the true type

MOLECULE_IDENTIFIER = str  # typing.NewType('MOLECULE_IDENTIFIER', str)
SMILES = str  # typing.NewType('SMILES', str)
CANON_SMILES = SMILES  # typing.NewType('CANON_SMILES', SMILES)  # This is for SMILES canonicalised by RDKit

RXN_STR = str  # typing.NewType('RXN_STR', str)

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

YIELD = float  # typing.NewType('YIELD', float)
YIELDS = typing.List[typing.Optional[YIELD]]

TEMPERATURE_CELCIUS = float  # typing.NewType('TEMPERATURE_CELCIUS', float)
TEMPERATURES_CELCIUS = typing.List[typing.Optional[TEMPERATURE_CELCIUS]]

RXN_TIME = float  # typing.NewType('RXN_TIME', float)  # hours
