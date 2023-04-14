from typing import List, Dict, Callable, Set, Optional
import pytest
import pathlib

from ord_schema.proto import reaction_pb2 as ord_reaction_pb2

from orderly.types import YIELD, MANUAL_REPLACEMENTS_DICT

REPETITIONS = 3
SLOW_REPETITIONS = 1


def test_hello_world() -> None:
    assert True


def get_rxn_func() -> Callable[[str, int], ord_reaction_pb2.Reaction]:
    from ord_schema.proto import reaction_pb2 as ord_reaction_pb2

    def get_rxn(
        file_name: str,
        rxn_idx: int,
    ) -> ord_reaction_pb2.Reaction:
        import orderly.extract.extractor
        import orderly.data.test_data
        import orderly.extract.main

        _file = orderly.extract.main.get_file_names(
            directory=orderly.data.test_data.get_path_of_test_ords(),
            file_ending=f"{file_name}.pb.gz",
        )
        assert len(_file) == 1
        file = pathlib.Path(_file[0])

        dataset = orderly.extract.extractor.OrdExtractor.load_data(file)
        rxn = dataset.reactions[rxn_idx]
        return rxn

    return get_rxn


@pytest.mark.parametrize(
    "file_name,rxn_idx,expected_labelled_reactants,expected_labelled_reagents,expected_labelled_solvents,expected_labelled_catalysts,expected_labelled_products_from_input,expected_non_smiles_names_list_additions",
    (
        [
            "ord_dataset-00005539a1e04c809a9a78647bea649c",
            0,
            ["CC(C)N1CCNCC1", "CCOC(=O)c1cnc2cc(OCC)c(Br)cc2c1Nc1ccc(F)cc1F"],
            ["O=C([O-])[O-]", "[Cs+]", "[Cs+]"],
            [],
            [
                "c1ccc(P(c2ccccc2)c2ccc3ccccc3c2-c2c(P(c3ccccc3)c3ccccc3)ccc3ccccc23)cc1",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "[Pd]",
                "[Pd]",
            ],
            [],
            [],
        ],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            0,
            [
                "SCc1ccccc1",
                "[H-]",
                "[Na+]",
                "O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1[N+](=O)[O-]",
            ],
            [],
            ["C1CCOC1", "C1CCOC1"],
            [],
            [],
            [],
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            [
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "35(Na2O)",
            ],
            [],
            ["O"],
            [],
            [],
            ["35(Na2O)"],
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            ["CC1(C)C2CCC(=O)C1C2", "C1CCNC1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            [],
            ["c1ccccc1"],
            [],
            [],
            [],
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_rxn_input_extractor(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    expected_labelled_reactants: List[str],
    expected_labelled_reagents: List[str],
    expected_labelled_solvents: List[str],
    expected_labelled_catalysts: List[str],
    expected_labelled_products_from_input: List[str],
    expected_non_smiles_names_list_additions: List[str],
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    import orderly.extract.extractor

    (
        labelled_reactants,
        labelled_reagents,
        labelled_solvents,
        labelled_catalysts,
        labelled_products_from_input,  # Daniel: I'm not sure what to do with this, it doesn't make sense for people to have put a product as an input, so this list should be empty anyway
        non_smiles_names_list_additions,
    ) = orderly.extract.extractor.OrdExtractor.rxn_input_extractor(rxn)

    assert sorted(expected_labelled_reactants) == sorted(
        labelled_reactants
    ), f"failure for {sorted(expected_labelled_reactants)=}, got {sorted(labelled_reactants)}"  # TODO unsure why we have random ordering on ubuntu
    assert (
        expected_labelled_reagents == labelled_reagents
    ), f"failure for {expected_labelled_reagents=}, got {labelled_reagents}"
    assert (
        expected_labelled_solvents == labelled_solvents
    ), f"failure for {expected_labelled_solvents=}, got {labelled_solvents}"
    assert (
        expected_labelled_catalysts == labelled_catalysts
    ), f"failure for {expected_labelled_catalysts=}, got {labelled_catalysts}"
    assert (
        expected_labelled_products_from_input == labelled_products_from_input
    ), f"failure for {expected_labelled_products_from_input=}, got {labelled_products_from_input}"
    assert (
        expected_non_smiles_names_list_additions == non_smiles_names_list_additions
    ), f"failure for {expected_non_smiles_names_list_additions=}, got {non_smiles_names_list_additions}"


@pytest.mark.parametrize(
    "file_name,rxn_idx,expected_labelled_products,expected_yields,expected_non_smiles_names_list_additions",
    (
        [
            "ord_dataset-00005539a1e04c809a9a78647bea649c",
            0,
            ["CCOC(=O)c1cnc2cc(OCC)c(N3CCN(C(C)C)CC3)cc2c1Nc1ccc(F)cc1F"],
            [65.39],
            [],
        ],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            0,
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            [None],
            [],
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            ["[O-]B1OB2OB([O-])OB(O1)O2", "[Na+]", "[Na+]"],
            [None, None, None],
            [],
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            [95.0],
            [],
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_rxn_outcomes_extractor(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    expected_labelled_products: List[str],
    expected_yields: List[Optional[float]],
    expected_non_smiles_names_list_additions: List[str],
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    import orderly.extract.extractor

    (
        labelled_products,
        yields,
        non_smiles_names_list_additions,
    ) = orderly.extract.extractor.OrdExtractor.rxn_outcomes_extractor(rxn)

    assert expected_yields == yields, f"failure for {expected_yields=} got {yields}"
    assert (
        expected_labelled_products == labelled_products
    ), f"failure for {expected_labelled_products=} got {labelled_products}"
    assert (
        expected_non_smiles_names_list_additions == non_smiles_names_list_additions
    ), f"failure for {expected_non_smiles_names_list_additions=} got {non_smiles_names_list_additions}"


@pytest.mark.parametrize(
    "file_name,rxn_idx,expected_rxn_str,expected_is_mapped",
    (
        ["ord_dataset-00005539a1e04c809a9a78647bea649c", 0, None, None],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            0,
            "[CH2:1]([SH:8])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1.[H-].[Na+].[Cl:11][C:12]1[CH:30]=[C:29]([C:31]([F:34])([F:33])[F:32])[CH:28]=[CH:27][C:13]=1[O:14][C:15]1[CH:20]=[CH:19][C:18]([N+:21]([O-:23])=[O:22])=[C:17]([N+]([O-])=O)[CH:16]=1>O1CCCC1>[CH2:1]([S:8][C:17]1[CH:16]=[C:15]([O:14][C:13]2[CH:27]=[CH:28][C:29]([C:31]([F:34])([F:32])[F:33])=[CH:30][C:12]=2[Cl:11])[CH:20]=[CH:19][C:18]=1[N+:21]([O-:23])=[O:22])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1",
            True,
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            "[B:1]([O-:4])([O-:3])[O-:2].[B:5]([O-:8])([O-:7])[O-:6].[B:9]([O-:12])([O-])[O-].[B:13]([O-])([O-])[O-].[Na+:17].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+]>O>[B:1]1([O-:4])[O:3][B:13]2[O:12][B:9]([O:6][B:5]([O-:8])[O:7]2)[O:2]1.[Na+:17].[Na+:17]",
            True,
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            "[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH2:5][C:6]2=O.[NH:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1.C1(C)C=CC(S(O)(=O)=O)=CC=1.O>C1C=CC=CC=1>[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH:5]=[C:6]2[N:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1",
            True,
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_rxn_string_and_is_mapped(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    expected_rxn_str: Optional[str],
    expected_is_mapped: Optional[bool],
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    import orderly.extract.extractor

    rxn_str_output = (
        orderly.extract.extractor.OrdExtractor.get_rxn_string_and_is_mapped(rxn)
    )
    if rxn_str_output is None:
        rxn_str, is_mapped = None, None
    else:
        rxn_str, is_mapped = rxn_str_output

    assert expected_rxn_str == rxn_str, f"failure for {expected_rxn_str=} got {rxn_str}"
    assert (
        expected_is_mapped == is_mapped
    ), f"failure for {expected_is_mapped=} got {is_mapped}"


@pytest.mark.parametrize(
    "file_name,rxn_idx,rxn_overwrite,expected_rxn_str_reactants,expected_rxn_str_agents,expected_rxn_str_products,expected_rxn_str,expected_non_smiles_names_list_additions,expected_none",
    (
        [
            "ord_dataset-00005539a1e04c809a9a78647bea649c",
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            True,
        ],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            0,
            None,
            [
                "O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1[N+](=O)[O-]",
                "SCc1ccccc1",
            ],
            [
                "C1CCOC1",
                "[H-]",
                "[Na+]",
            ],
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            "[CH2:1]([SH:8])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1.[H-].[Na+].[Cl:11][C:12]1[CH:30]=[C:29]([C:31]([F:34])([F:33])[F:32])[CH:28]=[CH:27][C:13]=1[O:14][C:15]1[CH:20]=[CH:19][C:18]([N+:21]([O-:23])=[O:22])=[C:17]([N+]([O-])=O)[CH:16]=1>O1CCCC1>[CH2:1]([S:8][C:17]1[CH:16]=[C:15]([O:14][C:13]2[CH:27]=[CH:28][C:29]([C:31]([F:34])([F:32])[F:33])=[CH:30][C:12]=2[Cl:11])[CH:20]=[CH:19][C:18]=1[N+:21]([O-:23])=[O:22])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1",
            [],
            False,
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            None,
            [
                "[O-]B([O-])[O-]",
            ],
            [
                "O",
                "[Na+]",
            ],
            [
                "[O-]B1OB2OB([O-])OB(O1)O2",
            ],
            "[B:1]([O-:4])([O-:3])[O-:2].[B:5]([O-:8])([O-:7])[O-:6].[B:9]([O-:12])([O-])[O-].[B:13]([O-])([O-])[O-].[Na+:17].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+]>O>[B:1]1([O-:4])[O:3][B:13]2[O:12][B:9]([O:6][B:5]([O-:8])[O:7]2)[O:2]1.[Na+:17].[Na+:17]",
            [],
            False,
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            None,
            [
                "C1CCNC1",
                "CC1(C)C2CCC(=O)C1C2",
            ],
            ["Cc1ccc(S(=O)(=O)O)cc1", "O", "c1ccccc1"],
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            "[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH2:5][C:6]2=O.[NH:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1.C1(C)C=CC(S(O)(=O)=O)=CC=1.O>C1C=CC=CC=1>[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH:5]=[C:6]2[N:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1",
            [],
            False,
        ],
        # Test case where reaction with only 1 >
        pytest.param(
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            "CC.C>CCC",
            ["CC", "C"],
            [],
            ["CCC"],
            "CC.C>CCC",
            [],
            False,
            marks=pytest.mark.xfail(
                reason="ValueError: not enough values to unpack (expected 3, got 2)"
            ),
        ),
        # There's no point in trying to test whether the the rxn.identifiers[0].value = None because the schema doesn't allow that overwrite to happen!
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_extract_info_from_rxn(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    rxn_overwrite: Optional[bool],
    expected_rxn_str_reactants: Optional[List[str]],
    expected_rxn_str_agents: Optional[List[str]],
    expected_rxn_str_products: Optional[List[str]],
    expected_rxn_str: Optional[str],
    expected_non_smiles_names_list_additions: Optional[List[str]],
    expected_none: bool,
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    if rxn_overwrite is not None:
        rxn.identifiers[0].value = rxn_overwrite

    import orderly.extract.extractor

    rxn_info = orderly.extract.extractor.OrdExtractor.extract_info_from_rxn(rxn)
    if expected_none:
        assert rxn_info is None, f"expected a none but got {rxn_info=}"
        return
    else:
        assert rxn_info is not None, f"did not expect a none but got one {rxn_info=}"
    (
        rxn_str_reactants,
        rxn_str_agents,
        rxn_str_products,
        rxn_str,
        non_smiles_names_list_additions,
    ) = rxn_info

    assert expected_rxn_str_reactants is not None
    assert expected_rxn_str_agents is not None
    assert expected_rxn_str_products is not None
    assert expected_rxn_str is not None
    assert expected_non_smiles_names_list_additions is not None

    assert expected_rxn_str_reactants == rxn_str_reactants
    assert expected_rxn_str_agents == rxn_str_agents
    assert expected_rxn_str_products == rxn_str_products
    assert expected_rxn_str == rxn_str
    assert expected_non_smiles_names_list_additions == non_smiles_names_list_additions


@pytest.mark.parametrize(
    "file_name,rxn_idx,expected_temperature",
    (
        [
            "ord_dataset-00005539a1e04c809a9a78647bea649c",
            0,
            110.0,
        ],
        ["ord_dataset-0b70410902ae4139bd5d334881938f69", 0, None],
        ["ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c", 0, 1100.0],
        ["ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6", 0, None],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_temperature_extractor(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    expected_temperature: Optional[float],
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    import orderly.extract.extractor

    temperature = orderly.extract.extractor.OrdExtractor.temperature_extractor(rxn)

    assert (
        expected_temperature == temperature
    ), f"failure for {expected_temperature=} got {temperature}"
    if temperature is not None:
        assert isinstance(
            temperature, float
        ), f"expected a float but got {temperature=}"


@pytest.mark.parametrize(
    "file_name,rxn_idx,expected_rxn_time",
    (
        ["ord_dataset-00005539a1e04c809a9a78647bea649c", 0, None],
        ["ord_dataset-0b70410902ae4139bd5d334881938f69", 0, None],
        ["ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c", 0, 0.17],
        ["ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6", 0, None],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_time_extractor(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    expected_rxn_time: Optional[float],
) -> None:
    rxn = get_rxn_func()(file_name, rxn_idx)

    import orderly.extract.extractor

    rxn_time = orderly.extract.extractor.OrdExtractor.rxn_time_extractor(rxn)

    assert (
        expected_rxn_time == rxn_time
    ), f"failure for {expected_rxn_time=} got {rxn_time=}"

    if rxn_time is not None:
        assert isinstance(rxn_time, float), f"expected a float but got {rxn_time=}"


@pytest.mark.parametrize(
    "rxn_str_agents,labelled_catalysts,labelled_solvents,labelled_reagents,metals,solvents_set,expected_agents,expected_solvents",
    (
        [
            None,
            [
                "c1ccc(P(c2ccccc2)c2ccc3ccccc3c2-c2c(P(c3ccccc3)c3ccccc3)ccc3ccccc23)cc1",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "[Pd]",
            ],
            [],
            ["O=C([O-])[O-]", "[Cs+]"],
            None,
            None,
            [
                "[Cs+]",
                "[Pd]",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "O=C([O-])[O-]",
                "c1ccc(P(c2ccccc2)c2ccc3ccccc3c2-c2c(P(c3ccccc3)c3ccccc3)ccc3ccccc23)cc1",
            ],
            [],
        ],
        [["C1CCOC1"], None, ["C1CCOC1", "C1CCOC1"], None, None, None, [], ["C1CCOC1"]],
        [["O"], [], ["O"], [], None, None, [], ["O"]],
        [
            ["c1ccccc1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            [],
            ["c1ccccc1"],
            [],
            None,
            None,
            ["Cc1ccc(S(=O)(=O)O)cc1"],
            ["O", "c1ccccc1"],
        ],
        # Made up test cases:
        [
            [
                "c1ccccc1",
                "Cc1ccc(S(=O)(=O)O)cc1",
                "O",
                None,
            ],  # TODO we should consider removing this none
            ["[Pd]"],
            ["O", "CCO"],
            ["O=C([O-])[O-]"],
            None,
            None,
            ["[Pd]", "Cc1ccc(S(=O)(=O)O)cc1", "O=C([O-])[O-]"],
            ["CCO", "O", "c1ccccc1"],
        ],
        pytest.param(
            ["c1ccccc1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            ["[Pd]"],
            ["O", "CCO"],
            ["O=C([O-])[O-]"],
            None,
            None,
            ["c1ccccc1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            ["O", "CCO"],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            ["c1ccccc1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            ["[Pd]"],
            ["O", "CCO"],
            ["O=C([O-])[O-]"],
            None,
            None,
            ["[Pd]", "Cc1ccc(S(=O)(=O)O)cc1", "O=C([O-])[O-]", "O", "CCO", "c1ccccc1"],
            [],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            ["c1ccccc1", "Cc1ccc(S(=O)(=O)O)cc1", "O"],
            ["[Pd]"],
            ["O", "CCO"],
            ["O=C([O-])[O-]"],
            None,
            None,
            ["[Pd]", "Cc1ccc(S(=O)(=O)O)cc1", "O=C([O-])[O-]"],
            ["O", "O", "CCO", "c1ccccc1"],
            marks=pytest.mark.xfail,
        ),
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_merge_to_agents(
    execution_number: int,
    rxn_str_agents: Optional[List[str]],
    labelled_catalysts: Optional[List[str]],
    labelled_solvents: Optional[List[str]],
    labelled_reagents: Optional[List[str]],
    metals: List[str],
    solvents_set: Set[str],
    expected_agents: Optional[List[str]],
    expected_solvents: Optional[List[str]],
) -> None:
    import orderly.extract.extractor
    import orderly.extract.defaults

    if metals is None:
        metals = orderly.extract.defaults.get_metals_list()
    if solvents_set is None:
        solvents_set = orderly.extract.defaults.get_solvents_set()

    agents, solvents = orderly.extract.extractor.OrdExtractor.merge_to_agents(
        rxn_str_agents,
        labelled_catalysts,
        labelled_solvents,
        labelled_reagents,
        metals,
        solvents_set,
    )

    assert expected_agents == agents, f"failure for {expected_agents=} got {agents}"
    assert (
        expected_solvents == solvents
    ), f"failure for {expected_solvents=} got {solvents}"


@pytest.mark.parametrize(
    "rxn_str_products,labelled_products,input_yields,expected_products,expected_yields",
    (
        [
            [],
            ["CCOC(=O)c1cnc2cc(OCC)c(N3CCN(C(C)C)CC3)cc2c1Nc1ccc(F)cc1F"],
            [65.39],
            ["CCOC(=O)c1cnc2cc(OCC)c(N3CCN(C(C)C)CC3)cc2c1Nc1ccc(F)cc1F"],
            [65.39],
        ],
        [
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            None,
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            None,
        ],
        [
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            [None, None, None],
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            [None, None, None],
        ],
        pytest.param(
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            [None],
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            [None],
            marks=pytest.mark.xfail(reason="IndexError: list index out of range"),
        ),
        [
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            ["[Na+]", "[Na+]", "[O-]B1OB2OB([O-])OB(O1)O2"],
            [None, None, None],
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            [None],
        ],
        [
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            [95.0],
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            [95.0],
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_match_yield_with_product(
    execution_number: int,
    rxn_str_products: List[str],
    labelled_products: List[str],
    input_yields: Optional[List[Optional[YIELD]]],
    expected_products: List[str],
    expected_yields: Optional[List[Optional[YIELD]]],
) -> None:
    import orderly.extract.extractor

    products, yields = orderly.extract.extractor.OrdExtractor.match_yield_with_product(
        rxn_str_products, labelled_products, input_yields
    )

    assert (
        expected_products == products
    ), f"failure for {expected_products=} got {products=}"
    assert expected_yields == yields, f"failure for {expected_yields=} got {yields=}"


@pytest.mark.parametrize(
    "file_name,rxn_idx,manual_replacements_dict,trust_labelling,expected_reactants, expected_agents, expected_reagents,expected_solvents,expected_catalysts,expected_products,expected_yields,expected_temperature,expected_rxn_time,expected_rxn_str, expected_procedure_details, expected_names_list",
    (
        [
            "ord_dataset-00005539a1e04c809a9a78647bea649c",
            0,
            {},
            False,
            ["CC(C)N1CCNCC1", "CCOC(=O)c1cnc2cc(OCC)c(Br)cc2c1Nc1ccc(F)cc1F"],
            [
                "[Cs+]",
                "[Pd]",
                "O=C(/C=C/c1ccccc1)/C=C/c1ccccc1",
                "O=C([O-])[O-]",
                "c1ccc(P(c2ccccc2)c2ccc3ccccc3c2-c2c(P(c3ccccc3)c3ccccc3)ccc3ccccc23)cc1",
            ],
            [],
            [],
            [],
            ["CCOC(=O)c1cnc2cc(OCC)c(N3CCN(C(C)C)CC3)cc2c1Nc1ccc(F)cc1F"],
            [65.39],
            110.0,
            None,
            None,
            "To a solution of ethyl 6-bromo-4-(2,4-difluorophenylamino)-7-ethoxyquinoline-3-carboxylate (400 mg, 0.89 mmol) and 1-(Isopropyl)piperazine (254 µl, 1.77 mmol) in dioxane was added cesium carbonate (722 mg, 2.22 mmol), tris(dibenzylideneacetone)dipalladium(0) (40.6 mg, 0.04 mmol) and rac-2,2'-Bis(diphenylphosphino)-1,1'-binaphthyl (55.2 mg, 0.09 mmol). Reaction vessel in oil bath set to 110 °C. 11am  After 5 hours, MS shows product (major peak 499), and SM (minor peak 453).  o/n, MS shows product peak. Reaction cooled, concentrated onto silica, and purified on ISCO. 40g column, 1:1 EA:Hex, then 100% EA.  289mg yellow solid. NMR (EN00180-62-1) supports product, but some oxidised BINAP impurity (LCMS 655).  ",
            [],
        ],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            0,
            {},
            False,
            [
                "SCc1ccccc1",
                "O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1[N+](=O)[O-]",
            ],
            ["[Na+]", "[H-]"],
            [],
            ["C1CCOC1"],
            [],
            ["O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1"],
            [None],
            None,
            None,
            "[CH2:1]([SH:8])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1.[H-].[Na+].[Cl:11][C:12]1[CH:30]=[C:29]([C:31]([F:34])([F:33])[F:32])[CH:28]=[CH:27][C:13]=1[O:14][C:15]1[CH:20]=[CH:19][C:18]([N+:21]([O-:23])=[O:22])=[C:17]([N+]([O-])=O)[CH:16]=1>O1CCCC1>[CH2:1]([S:8][C:17]1[CH:16]=[C:15]([O:14][C:13]2[CH:27]=[CH:28][C:29]([C:31]([F:34])([F:32])[F:33])=[CH:30][C:12]=2[Cl:11])[CH:20]=[CH:19][C:18]=1[N+:21]([O-:23])=[O:22])[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1",
            "1.7 g of benzyl mercaptan was dissolved in dry tetrahydrofuran and 0.5 g of sodium hydride added with stirring under dry nitrogen. The reaction mixture was stirred under reflux for 30 minutes, and a solution of 5 g of 1A dissolved in 25 ml of dry tetrahydrofuran was added dropwise. Reaction occurred rapidly, and the product was chromatographically purified to give 2-benzylthio-4-(2-chloro-4-trifluoromethylphenoxy)nitrobenzene (1B) as a yellow oil.",
            [],
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            {},
            False,
            ["[O-]B([O-])[O-]"],
            ["35(Na2O)", "[Na+]"],
            [],
            ["O"],
            [],
            ["[O-]B1OB2OB([O-])OB(O1)O2"],
            [None],
            1100.0,
            0.17,
            "[B:1]([O-:4])([O-:3])[O-:2].[B:5]([O-:8])([O-:7])[O-:6].[B:9]([O-:12])([O-])[O-].[B:13]([O-])([O-])[O-].[Na+:17].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+]>O>[B:1]1([O-:4])[O:3][B:13]2[O:12][B:9]([O:6][B:5]([O-:8])[O:7]2)[O:2]1.[Na+:17].[Na+:17]",
            "Sodium tetraborate (Na2B4O7.10H2O), analyzed reagent was dried overnight at 150° C, mixed with the appropriate quantity of dopant ions and homogenized in an electric homogenizer (vibrator) during 10 minutes. The material was then transferred to a platinum crucible and heated at 1100° C for at least 30 minutes, until a clear transparent solution was obtained. The glass matrix loses water and the composition of the matrix is after the heating 35(Na2O).65(B2O3). A drop of the hot melt was allowed to fall directly onto a clean white glazed ceramic surface, into the center of a space ring of 1 mm thickness, and pressed with a second ceramic tile to produce a glass disk of 1 mm thickness and an approximate diameter of 12 mm. The glass is transparent in the ultraviolet and in the visible part of the spectrum.",
            ["35(Na2O)"],
        ],
        [
            "ord_dataset-0bb2e99daa66408fb8dbd6a0781d241c",
            0,
            {},
            True,
            [
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[Na+]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "[O-]B([O-])[O-]",
                "35(Na2O)",
            ],
            [],
            [],
            ["O"],
            [],
            [
                "[O-]B1OB2OB([O-])OB(O1)O2",
                "[Na+]",
                "[Na+]",
            ],
            [None, None, None],
            1100.0,
            0.17,
            "[B:1]([O-:4])([O-:3])[O-:2].[B:5]([O-:8])([O-:7])[O-:6].[B:9]([O-:12])([O-])[O-].[B:13]([O-])([O-])[O-].[Na+:17].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+].[Na+]>O>[B:1]1([O-:4])[O:3][B:13]2[O:12][B:9]([O:6][B:5]([O-:8])[O:7]2)[O:2]1.[Na+:17].[Na+:17]",
            "Sodium tetraborate (Na2B4O7.10H2O), analyzed reagent was dried overnight at 150° C, mixed with the appropriate quantity of dopant ions and homogenized in an electric homogenizer (vibrator) during 10 minutes. The material was then transferred to a platinum crucible and heated at 1100° C for at least 30 minutes, until a clear transparent solution was obtained. The glass matrix loses water and the composition of the matrix is after the heating 35(Na2O).65(B2O3). A drop of the hot melt was allowed to fall directly onto a clean white glazed ceramic surface, into the center of a space ring of 1 mm thickness, and pressed with a second ceramic tile to produce a glass disk of 1 mm thickness and an approximate diameter of 12 mm. The glass is transparent in the ultraviolet and in the visible part of the spectrum.",
            ["35(Na2O)"],
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            {},
            False,
            [
                "CC1(C)C2CCC(=O)C1C2",
                "C1CCNC1",
            ],
            [
                "Cc1ccc(S(=O)(=O)O)cc1",
            ],
            [],
            [
                "O",
                "c1ccccc1",
            ],
            [],
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            [95.0],
            None,
            None,
            "[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH2:5][C:6]2=O.[NH:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1.C1(C)C=CC(S(O)(=O)=O)=CC=1.O>C1C=CC=CC=1>[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH:5]=[C:6]2[N:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1",
            "A solution of 30 g of nopinone ([α]D20 =+39.90; c=8 in ethanol), 29 of pyrrolidine and 0.4 g of p-toluenesulfonic acid in 150 ml anhydrous benzene was heated at reflux for 40 h under nitrogen atmosphere in a vessel fitted with a water separator. After evaporation of the solvent and distillation of the residue, there were obtained 39.5 g (95% yield) of 1-(6,6-dimethylnorpin-2-en-2-yl)-pyrrolidine having b.p. 117°-118° C./10 Torr.",
            [],
        ],
        [
            "ord_dataset-0bf72e95d80743729fdbb8b57a4bc0c6",
            0,
            {},
            True,
            [
                "C1CCNC1",
                "CC1(C)C2CCC(=O)C1C2",
                "O",
                "Cc1ccc(S(=O)(=O)O)cc1",
            ],
            [],
            [],
            ["c1ccccc1"],
            [],
            ["CC1(C)C2CC=C(N3CCCC3)C1C2"],
            [95.0],
            None,
            None,
            "[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH2:5][C:6]2=O.[NH:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1.C1(C)C=CC(S(O)(=O)=O)=CC=1.O>C1C=CC=CC=1>[CH3:1][C:2]1([CH3:10])[CH:8]2[CH2:9][CH:3]1[CH2:4][CH:5]=[C:6]2[N:11]1[CH2:15][CH2:14][CH2:13][CH2:12]1",
            "A solution of 30 g of nopinone ([α]D20 =+39.90; c=8 in ethanol), 29 of pyrrolidine and 0.4 g of p-toluenesulfonic acid in 150 ml anhydrous benzene was heated at reflux for 40 h under nitrogen atmosphere in a vessel fitted with a water separator. After evaporation of the solvent and distillation of the residue, there were obtained 39.5 g (95% yield) of 1-(6,6-dimethylnorpin-2-en-2-yl)-pyrrolidine having b.p. 117°-118° C./10 Torr.",
            [],
        ],
        # Test: one of the input reactants = 'liquid'; trust_labelling = True
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            3,
            {},
            True,
            ["Clc1nc(Cl)nc(Cl)n1", "N"],
            [],
            [],
            ["C1CCOC1", "COCCOCCOC"],
            [],
            ["Nc1nc(Cl)nc(Cl)n1"],
            [None],
            25,
            1.0,
            "[N:1]1[C:8]([Cl:9])=[N:7][C:5]([Cl:6])=[N:4][C:2]=1Cl.[NH3:10]>C1COCC1.COCCOCCOC>[NH2:10][C:2]1[N:1]=[C:8]([Cl:9])[N:7]=[C:5]([Cl:6])[N:4]=1",
            "A solution of 300 g (1.63 mol) of cyanuric chloride in 1 liter THF and 0.24 liter diglyme was cooled to 0\302\260 C. and 81.6 mL (3.36 mol) of liquid ammonia added dropwise over 90 min. keeping the temperature between 10\302\260-15\302\260. The mixture was stirred for one hour at -10\302\260 to 0\302\260 and then allowed to warm to ambient temperature over one hour. The resulting suspension was filtered, the solid washed with THF, the filtrate reduced to 1/2 its original volume, and poured over 1 liter of ice water to give a white solid which was collected, washed with water, and dried in vacuo to give 244.3 g of 2-amino-4,6-dichloro-1,3,5-triazine with m.p. 221\302\260-223.5\302\260 (dec).",
            ["liquid"],
        ],
        # Test: one of the input reactants = 'liquid'; trust_labelling = False
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            3,
            {},
            False,
            ["Clc1nc(Cl)nc(Cl)n1", "N"],
            [],
            [],
            ["C1CCOC1", "COCCOCCOC"],
            [],
            ["Nc1nc(Cl)nc(Cl)n1"],
            [None],
            25,
            1.0,
            "[N:1]1[C:8]([Cl:9])=[N:7][C:5]([Cl:6])=[N:4][C:2]=1Cl.[NH3:10]>C1COCC1.COCCOCCOC>[NH2:10][C:2]1[N:1]=[C:8]([Cl:9])[N:7]=[C:5]([Cl:6])[N:4]=1",
            "A solution of 300 g (1.63 mol) of cyanuric chloride in 1 liter THF and 0.24 liter diglyme was cooled to 0\302\260 C. and 81.6 mL (3.36 mol) of liquid ammonia added dropwise over 90 min. keeping the temperature between 10\302\260-15\302\260. The mixture was stirred for one hour at -10\302\260 to 0\302\260 and then allowed to warm to ambient temperature over one hour. The resulting suspension was filtered, the solid washed with THF, the filtrate reduced to 1/2 its original volume, and poured over 1 liter of ice water to give a white solid which was collected, washed with water, and dried in vacuo to give 244.3 g of 2-amino-4,6-dichloro-1,3,5-triazine with m.p. 221\302\260-223.5\302\260 (dec).",
            ["liquid"],
        ],
        # synthesis of islatravir by biocatalytic cascade
        # We put trust_labelling = False to test that the inputs are extracted instead, since I know that there's no rxn string
        [
            "ord_dataset-6a0bfcdf53a64c07987822162ae591e2",
            0,
            {},
            False,
            ["C#CC(O)(CO)CO"],
            [
                "[Cu+2]",
                "[K+]",
                "Antifoam 204",
                "O=S(=O)([O-])CCN1CCN(CCS(=O)(=O)[O-])CC1",
                "O=S(=O)([O-])[O-]",
                "bovine catalase",
                "evolved galactose oxidase GOase-Rd13BB",
                "horseradish peroxidase",
            ],
            [],
            ["O"],
            [],
            ["C#C[C@](O)(C=O)CO"],
            [68.0],
            25.0,
            22.0,
            None,
            "",
            [
                "Antifoam 204",
                "bovine catalase",
                "evolved galactose oxidase GOase-Rd13BB",
                "horseradish peroxidase",
            ],
        ],
        # An example where we need the manual_replacements_dict
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            982,
            {},
            True,
            [
                "CCO",
                "O",
                "COc1ccccc1C(O)c1cccc(Br)n1",
                "O=[Cr](=O)=O",
            ],
            [],
            [],
            ["CC(=O)O"],
            [],
            ["COc1ccccc1C(=O)c1cccc(Br)n1"],
            [66.2],
            None,
            None,
            "[Br:1][C:2]1[N:7]=[C:6]([CH:8]([C:10]2[CH:15]=[CH:14][CH:13]=[CH:12][C:11]=2[O:16][CH3:17])[OH:9])[CH:5]=[CH:4][CH:3]=1.C(O)C.O>C(O)(=O)C>[Br:1][C:2]1[N:7]=[C:6]([C:8](=[O:9])[C:10]2[CH:15]=[CH:14][CH:13]=[CH:12][C:11]=2[O:16][CH3:17])[CH:5]=[CH:4][CH:3]=1",
            "By the same procedure of Ex. 22, and reacting 3.3 g 6-bromo-\316\261-(2-methoxyphenyl)-2-pyridinemethanol (obtained as in Ex. 19) in 20 ml glacial acetic acid with CrO3 (1 g in 5 ml water), there is obtained 2.17 g title product, m.p. 97\302\260-8\302\260 C. (ethanol:water); UV (ethanol):\316\273max. 278 nm, \316\265: 12,480; Br 27.67 (27.36).",
            ["CrO3"],
        ],
        [
            "ord_dataset-0b70410902ae4139bd5d334881938f69",
            982,
            {},
            False,
            [
                "COc1ccccc1C(O)c1cccc(Br)n1",
            ],
            [
                "O=[Cr](=O)=O",
            ],
            [],
            ["CC(=O)O", "CCO", "O"],
            [],
            ["COc1ccccc1C(=O)c1cccc(Br)n1"],
            [66.2],
            None,
            None,
            "[Br:1][C:2]1[N:7]=[C:6]([CH:8]([C:10]2[CH:15]=[CH:14][CH:13]=[CH:12][C:11]=2[O:16][CH3:17])[OH:9])[CH:5]=[CH:4][CH:3]=1.C(O)C.O>C(O)(=O)C>[Br:1][C:2]1[N:7]=[C:6]([C:8](=[O:9])[C:10]2[CH:15]=[CH:14][CH:13]=[CH:12][C:11]=2[O:16][CH3:17])[CH:5]=[CH:4][CH:3]=1",
            "By the same procedure of Ex. 22, and reacting 3.3 g 6-bromo-\316\261-(2-methoxyphenyl)-2-pyridinemethanol (obtained as in Ex. 19) in 20 ml glacial acetic acid with CrO3 (1 g in 5 ml water), there is obtained 2.17 g title product, m.p. 97\302\260-8\302\260 C. (ethanol:water); UV (ethanol):\316\273max. 278 nm, \316\265: 12,480; Br 27.67 (27.36).",
            ["CrO3"],
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_handle_reaction_object(
    execution_number: int,
    file_name: str,
    rxn_idx: int,
    manual_replacements_dict: MANUAL_REPLACEMENTS_DICT,
    trust_labelling: bool,
    expected_reactants: List[str],
    expected_agents: List[str],
    expected_reagents: List[str],
    expected_solvents: List[str],
    expected_catalysts: List[str],
    expected_products: List[str],
    expected_yields: List[Optional[float]],
    expected_temperature: Optional[float],
    expected_rxn_time: Optional[float],
    expected_rxn_str: Optional[str],
    expected_procedure_details: str,
    expected_names_list: List[str],
) -> None:
    import orderly.extract.extractor
    import orderly.extract.main
    import orderly.extract.defaults

    rxn = get_rxn_func()(file_name, rxn_idx)
    if manual_replacements_dict == {}:
        manual_replacements_dict = orderly.extract.main.get_manual_replacements_dict(
            solvents_path=None
        )

    assert manual_replacements_dict is not None

    metals = orderly.extract.defaults.get_metals_list()
    solvents_set = orderly.extract.defaults.get_solvents_set()

    rnx_object = orderly.extract.extractor.OrdExtractor.handle_reaction_object(
        rxn, manual_replacements_dict, solvents_set, metals, trust_labelling
    )

    assert rnx_object is not None

    (
        reactants,
        agents,
        reagents,
        solvents,
        catalysts,
        products,
        yields,
        temperature,
        rxn_time,
        rxn_str,
        procedure_details,
        names_list,
    ) = rnx_object

    def clean_string(s: str) -> str:
        import string

        printable = set(string.printable)
        return "".join(filter(lambda x: x in printable, s))

    clean_procedure_details = clean_string(procedure_details)
    clean_expected_procedure_details = clean_string(expected_procedure_details)

    assert sorted(reactants) == sorted(
        expected_reactants
    ), f"failure for {sorted(expected_reactants)=} got {sorted(reactants)}"  # TODO unsure why we have random ordering on ubuntu
    assert agents == expected_agents, f"failure for {expected_agents=} got {agents}"
    assert (
        reagents == expected_reagents
    ), f"failure for {expected_reagents=} got {reagents}"
    assert (
        solvents == expected_solvents
    ), f"failure for {expected_solvents=} got {solvents}"
    assert (
        catalysts == expected_catalysts
    ), f"failure for {expected_catalysts=} got {catalysts}"
    assert (
        products == expected_products
    ), f"failure for {expected_products=} got {products}"
    assert yields == expected_yields, f"failure for {expected_yields=} got {yields}"
    assert (
        temperature == expected_temperature
    ), f"failure for {expected_temperature=} got {temperature}"
    assert (
        rxn_time == expected_rxn_time
    ), f"failure for {expected_rxn_time=} got {rxn_time}"
    assert rxn_str == expected_rxn_str, f"failure for {expected_rxn_str=} got {rxn_str}"
    assert (
        names_list == expected_names_list
    ), f"failure for {expected_names_list=} got {names_list}"
    assert (
        clean_procedure_details == clean_expected_procedure_details
    ), f"failure for {clean_expected_procedure_details=} got {clean_procedure_details}"


@pytest.mark.parametrize(
    "smiles,is_mapped,expected_canonical_smiles",
    (
        ["teststring", True, None],
        ["teststring", False, None],
        ["c1ccccc1", False, "c1ccccc1"],
        [
            "[CH2:1]([S:8][C:9]1[CH:14]=[C:13]([O:15][C:16]2[CH:21]=[CH:20][C:19]([C:22]([F:25])([F:24])[F:23])=[CH:18][C:17]=2[Cl:26])[CH:12]=[CH:11][C:10]=1[N+:27]([O-])=O)[C:2]1[CH:7]=[CH:6][CH:5]=[CH:4][CH:3]=1",
            True,
            "O=[N+]([O-])c1ccc(Oc2ccc(C(F)(F)F)cc2Cl)cc1SCc1ccccc1",
        ],
        ["P([O-])(O)O", False, "[O-]P(O)O"],
        [
            "[CC(C)(C)[P]([Pd][P](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C]",
            False,
            "CC(C)(C)[P]([Pd][P](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C",
        ],
        [
            "[CC(C)(C)[P]([Pd][P](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C]",
            True,
            "CC(C)(C)[P]([Pd][P](C(C)(C)C)(C(C)(C)C)C(C)(C)C)(C(C)(C)C)C(C)(C)C",
        ],
    ),
)
@pytest.mark.parametrize("execution_number", range(REPETITIONS))
def test_canonicalisation(
    execution_number: int,
    smiles: str,
    is_mapped: bool,
    expected_canonical_smiles: Optional[str],
) -> None:
    from orderly.extract.canonicalise import get_canonicalised_smiles

    canonical_smiles = get_canonicalised_smiles(smiles, is_mapped)

    assert (
        expected_canonical_smiles == canonical_smiles
    ), f"failure for {expected_canonical_smiles=} got {canonical_smiles}"


@pytest.mark.parametrize(
    "trust_labelling,use_multiprocessing,name_contains_substring,inverse_substring",
    (
        [False, True, "uspto", True],
        [
            False,
            True,
            "uspto",
            False,
        ],
        [True, False, "uspto", True],
        [True, True, None, True],
    ),
)
@pytest.mark.parametrize("execution_number", range(SLOW_REPETITIONS))
def test_extraction_pipeline(
    execution_number: int,
    tmp_path: pathlib.Path,
    trust_labelling: bool,
    use_multiprocessing: bool,
    name_contains_substring: Optional[str],
    inverse_substring: bool,
) -> None:
    extracted_ord_data_folder = "extracted_ord_data"
    (tmp_path / extracted_ord_data_folder).mkdir()
    molecule_names_folder = "molecule_names"
    (tmp_path / molecule_names_folder).mkdir()

    import orderly.extract.main
    import orderly.data.test_data

    orderly.extract.main.main(
        data_path=orderly.data.test_data.get_path_of_test_ords(),
        ord_file_ending=".pb.gz",
        trust_labelling=trust_labelling,
        output_path=tmp_path,
        extracted_ord_data_folder=extracted_ord_data_folder,
        solvents_path=None,
        molecule_names_folder=molecule_names_folder,
        merged_molecules_file="all_molecule_names.pkl",
        use_multiprocessing=use_multiprocessing,
        name_contains_substring=name_contains_substring,
        inverse_substring=inverse_substring,
        overwrite=False,
    )

    import pandas as pd
    import numpy as np

    for extraction in (tmp_path / extracted_ord_data_folder).glob("*"):
        df = pd.read_parquet(extraction)
        if df is None:
            continue

        # Columns: ['rxn_str_0', 'reactant_0', 'reactant_1', 'reactant_2', 'reactant_3', 'agent_0', 'agent_1', 'agent_2', 'agent_3', 'agent_4', 'agent_5', 'solvent_0', 'solvent_1', 'solvent_2', 'temperature_0', 'rxn_time_0', 'product_0', 'yield_0', 'grant_date'],
        # They're allowed to be strings or floats (depending on the col) or None
        for col in df.columns:
            series = df[col].replace({None: np.nan})
            if len(series.dropna()) == 0:
                continue
            elif col == "grant_date":
                continue  # TODO check that it is an optional datetime
            elif "temperature" in col or "rxn_time" in col or "yield" in col:
                assert pd.api.types.is_float_dtype(series), f"failure for {col=}"
            else:
                assert pd.api.types.is_string_dtype(series), f"failure for {col=}"
