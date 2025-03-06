import logging
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
from schema import SchemaError

from genelastic.import_data import (
    ImportBundle,
    load_import_bundle_file,
    make_import_bundle_from_files,
)

RES_DIR = Path(__file__).parent / "res"


def test_v1() -> None:
    files = (RES_DIR / "import_bundles").glob("v1_*.yml")

    # Loop on all test bundle files
    for f in files:
        bdl = make_import_bundle_from_files([f])
        assert isinstance(bdl, ImportBundle)


def test_v1_single_vcf() -> None:
    f = RES_DIR / "import_bundles" / "v1_single_vcf.yml"
    bdl_dicts = load_import_bundle_file(f)
    assert isinstance(bdl_dicts, list)
    assert len(bdl_dicts) == 1
    assert bdl_dicts[0]["version"] == 1
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_files("cov") == 0
    assert len(bdl.analyses) == 1
    assert bdl.analyses.get_nb_files() == 1
    assert bdl.analyses.get_nb_files("vcf") == 1
    assert bdl.analyses.get_nb_files("cov") == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v1_two_vcf_files() -> None:
    f = RES_DIR / "import_bundles" / "v1_two_vcf_files.yml"
    bdl_dicts = load_import_bundle_file(f)
    assert len(bdl_dicts) == 1
    assert bdl_dicts[0]["version"] == 1
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.get_nb_files("cov") == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v1_two_duplicated_vcf_files() -> None:
    f = RES_DIR / "import_bundles" / "v1_two_duplicated_vcf_files.yml"
    bdl_dicts = load_import_bundle_file(f)
    assert len(bdl_dicts) == 1
    assert bdl_dicts[0]["version"] == 1
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_files("cov") == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v2_file_pattern() -> None:
    f = RES_DIR / "import_bundles" / "v2_file_pattern.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_files("vcf")[0].metadata is not None
    assert "project_id" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["project_id"] == "H224"
    assert "sample_id" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["sample_id"] == "B00GXCZ"
    assert "flowcell_id" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["flowcell_id"] == "HJCTLCCXX"
    assert "lane" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["lane"] == "1"
    assert "sequencer_indices" in bdl.get_files("vcf")[0].metadata
    assert (
        bdl.get_files("vcf")[0].metadata["sequencer_indices"]
        == "IND1-IND2-IND3-IND4-IND5-IND6-IND7-IND8"
    )
    assert "ref" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["ref"] == "hs37d5"
    assert "depth" in bdl.get_files("vcf")[0].metadata
    assert bdl.get_files("vcf")[0].metadata["depth"] == "10"
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_file_pattern() -> None:
    f = RES_DIR / "import_bundles" / "v3_analyses.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_nb_matched_files() == 1
    assert bdl.get_nb_unmatched_files() == 0
    vcf_file = bdl.get_files("vcf")[0]
    assert vcf_file.metadata is not None
    assert vcf_file.metadata.get("sample_name") == "HG0003"
    assert vcf_file.metadata.get("source") == "CNRGH"
    assert vcf_file.metadata.get("barcode") == "C0034BP"
    assert vcf_file.metadata.get("wet_process") == "novaseqxplus-10b"
    assert vcf_file.metadata.get("bi_process") == "dragen-4123"
    assert vcf_file.metadata.get("reference_genome") == "hg38"
    assert vcf_file.metadata.get("cov_depth") == 30
    assert len(bdl.analyses) == 1
    assert bdl.analyses[0].metadata == {
        "barcode": "C0034BP",
        "sample_name": "HG0003",
        "source": "CNRGH",
        "wet_process": "novaseqxplus-10b",
        "bi_process": "dragen-4123",
        "reference_genome": "hg38",
        "cov_depth": 30,
        "lanes": [5],
        "flowcell": "22FC25LT3",
        "qc_comment": "",
        "seq_indices": ["DUAL219", "DUAL222", "DUAL225", "DUAL228", "DUAL289"],
    }
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_files_list() -> None:
    f = RES_DIR / "import_bundles" / "v3_files_list.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.get_nb_files("cov") == 1
    assert bdl.analyses.get_all_categories() == {"vcf", "cov"}


def test_v3_files_list_with_gz() -> None:
    f = RES_DIR / "import_bundles" / "v3_files_list_with_gz.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 3
    assert bdl.get_nb_files("cov") == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_empty_data_folder() -> None:
    f = RES_DIR / "import_bundles" / "v3_analyses_empty_folder.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 0
    assert bdl.get_nb_matched_files() == 0
    assert bdl.get_nb_unmatched_files() == 0
    assert bdl.analyses.get_all_categories() == set()


def test_v3_non_matching_files() -> None:
    f = RES_DIR / "import_bundles" / "v3_non_matching_files.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 0
    assert bdl.get_nb_matched_files() == 0
    assert bdl.get_nb_unmatched_files() == 3
    assert bdl.analyses.get_all_categories() == set()


def test_v3_one_matching_one_non_matching() -> None:
    f = RES_DIR / "import_bundles" / "v3_one_matching_one_non_matching.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_matched_files() == 1
    assert bdl.get_nb_unmatched_files() == 1
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_two_analyses() -> None:
    f = RES_DIR / "import_bundles" / "v3_two_analyses.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.get_nb_files("cov") == 0
    assert len(bdl.analyses) == 2
    assert bdl.analyses[0].get_nb_files() == 1
    assert bdl.analyses[1].get_nb_files() == 1
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_two_analyses_in_two_documents() -> None:
    f = RES_DIR / "import_bundles" / "v3_two_analyses_in_two_documents.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.get_nb_files("cov") == 0
    assert len(bdl.analyses) == 2
    assert bdl.analyses[0].get_nb_files() == 1
    assert bdl.analyses[1].get_nb_files() == 1
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_varying_coverage() -> None:
    f = RES_DIR / "import_bundles" / "v3_varying_coverage.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 4
    assert bdl.get_nb_files("cov") == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_several_dummy_files() -> None:
    files = (RES_DIR / "import_bundles").glob("v3_dummy*.yml")

    total_vcf_count = 0

    for file in files:
        bdl = make_import_bundle_from_files([file])
        assert bdl.analyses.get_all_categories() == {"vcf"}
        total_vcf_count += bdl.get_nb_files("vcf")

    assert total_vcf_count == 0


def test_v3_file_pattern_with_rep1() -> None:
    f_rep1 = RES_DIR / "import_bundles" / "v3_rep1.yml"
    bdl_rep1 = make_import_bundle_from_files([f_rep1])
    assert bdl_rep1.get_nb_files("vcf") == 1
    assert bdl_rep1.get_nb_files("cov") == 0
    assert bdl_rep1.get_nb_matched_files() == 1
    assert bdl_rep1.get_nb_unmatched_files() == 0
    assert bdl_rep1.analyses.get_all_categories() == {"vcf"}


def test_v3_file_pattern_with_custom_regex() -> None:
    f = RES_DIR / "import_bundles" / "v3_custom_regex.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 1
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_nb_matched_files() == 1
    assert bdl.get_nb_unmatched_files() == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_file_pattern_with_custom_end_of_file() -> None:
    f = RES_DIR / "import_bundles" / "v3_custom_regex_end_of_file.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 4
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_nb_matched_files() == 4
    assert bdl.get_nb_unmatched_files() == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_random_string_regex() -> None:
    f = RES_DIR / "import_bundles" / "v3_random_string_regex.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_nb_matched_files() == 2
    assert bdl.get_nb_unmatched_files() == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_no_analyses() -> None:
    f = RES_DIR / "import_bundles" / "v3_no_analyses.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.get_nb_files("vcf") == 0
    assert bdl.get_nb_files("cov") == 0
    assert bdl.get_nb_matched_files() == 0
    assert bdl.get_nb_unmatched_files() == 0
    assert bdl.analyses.get_all_categories() == set()


def test_v3_wet_processes_only_mandatory_keys() -> None:
    f = RES_DIR / "import_bundles" / "wet_processes" / "only_mandatory_keys.yml"
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 1
    assert wet_processes.get_process_ids() == {"wgs-novaseqxplus-25b"}


def test_v3_wet_processes_both_mandatory_and_optional_keys() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "wet_processes"
        / "both_mandatory_and_optional_keys.yml"
    )
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 1
    assert wet_processes.get_process_ids() == {"wgs-novaseqxplus-25b"}


def test_v3_wet_processes_optional_keys_partially_filled() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "wet_processes"
        / "optional_keys_partially_filled.yml"
    )
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 1
    assert wet_processes.get_process_ids() == {"wgs-novaseqxplus-25b"}


def test_v3_wet_processes_two_in_one_file() -> None:
    f = RES_DIR / "import_bundles" / "wet_processes" / "two_in_one_file.yml"
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 2
    assert wet_processes.get_process_ids() == {
        "wgs-novaseqxplus-25b",
        "wgs-novaseqxplus-10b",
    }


def test_v3_wet_processes_two_in_one_file_with_the_same_id() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "wet_processes"
        / "two_in_one_file_with_the_same_id.yml"
    )
    with pytest.raises(
        ValueError,
        match="A wet process with the id 'wgs-novaseqxplus-25b' is already present.",
    ):
        make_import_bundle_from_files([f])


def test_v3_wet_processes_mandatory_key_omitted() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "wet_processes"
        / "mandatory_key_omitted.yml"
    )
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert "Missing key: 'proc_id'" in str(exc_info.value)


def test_v3_wet_processes_empty_processes() -> None:
    f = RES_DIR / "import_bundles" / "wet_processes" / "empty_processes.yml"
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 0
    assert not wet_processes.get_process_ids()
    assert bdl.analyses.get_all_categories() == set()


def test_v3_wet_processes_no_processes() -> None:
    f = RES_DIR / "import_bundles" / "wet_processes" / "no_processes.yml"
    bdl = make_import_bundle_from_files([f])
    wet_processes = bdl.wet_processes
    assert len(wet_processes) == 0
    assert not wet_processes.get_process_ids()
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_only_mandatory_keys() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "only_mandatory_keys.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 1
    assert bi_processes.get_process_ids() == {"varscope-3"}
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_both_mandatory_and_optional_keys() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "bi_processes"
        / "both_mandatory_and_optional_keys.yml"
    )
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 1
    assert bi_processes.get_process_ids() == {"varscope-3"}
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_two_in_one_file() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "two_in_one_file.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 2
    assert bi_processes.get_process_ids() == {"varscope-3", "glimpse-2"}
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_two_in_one_file_with_the_same_id() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "bi_processes"
        / "two_in_one_file_with_the_same_id.yml"
    )
    with pytest.raises(
        ValueError,
        match="A bi process with the id 'varscope-3' is already present.",
    ):
        make_import_bundle_from_files([f])


def test_v3_bi_processes_mandatory_key_omitted() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "bi_processes"
        / "mandatory_key_omitted.yml"
    )
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert "Missing key: 'proc_id'" in str(exc_info.value)


def test_v3_bi_processes_empty_processes() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "empty_processes.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 0
    assert not bi_processes.get_process_ids()
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_no_processes() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "no_processes.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 0
    assert not bi_processes.get_process_ids()
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_null_steps() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "null_steps.yml"
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert "None should be instance of 'list'" in str(exc_info.value)


def test_v3_bi_processes_empty_steps() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "empty_steps.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 1
    assert bi_processes.get_process_ids() == {"varscope-3"}
    assert len(bi_processes["varscope-3"].data["steps"]) == 0
    assert bdl.analyses.get_all_categories() == set()


def test_v3_bi_processes_one_step() -> None:
    f = RES_DIR / "import_bundles" / "bi_processes" / "one_step.yml"
    bdl = make_import_bundle_from_files([f])
    bi_processes = bdl.bi_processes
    assert len(bi_processes) == 1
    assert bi_processes.get_process_ids() == {"varscope-3"}
    assert len(bi_processes["varscope-3"].data["steps"]) == 1
    assert bdl.analyses.get_all_categories() == set()


def test_v1_load_analysis_without_defined_bi_and_wet_processes() -> None:
    f = RES_DIR / "import_bundles" / "v1_single_vcf.yml"
    bdl = make_import_bundle_from_files([f], check=True)
    assert len(bdl.analyses) == 1
    assert bdl.get_nb_files("vcf") == 1
    assert len(bdl.wet_processes) == 0
    assert len(bdl.bi_processes) == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v2_load_analysis_without_defined_bi_and_wet_processes() -> None:
    f = RES_DIR / "import_bundles" / "v2_file_pattern.yml"
    bdl = make_import_bundle_from_files([f], check=True)
    assert len(bdl.analyses) == 1
    assert bdl.get_nb_files("vcf") == 1
    assert len(bdl.wet_processes) == 0
    assert len(bdl.bi_processes) == 0
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_load_analysis_with_defined_bi_and_wet_processes() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "multi"
        / "analysis_with_defined_bi_and_wet_processes.yml"
    )
    bdl = make_import_bundle_from_files([f], check=True)
    assert len(bdl.analyses) == 1
    assert bdl.get_nb_files("vcf") == 1
    assert len(bdl.wet_processes) == 1
    assert bdl.wet_processes.get_process_ids() == {"novaseqxplus-10b"}
    assert len(bdl.bi_processes) == 1
    assert bdl.bi_processes.get_process_ids() == {"dragen-4123"}
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_load_analysis_with_undefined_wet_process() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "multi"
        / "analysis_with_undefined_wet_process.yml"
    )

    with pytest.raises(SystemExit) as exc_info:
        make_import_bundle_from_files([f], check=True)

    assert (
        exc_info.value.code
        == f"Analysis at index 0 in file {f} is referencing "
        f"an undefined wet process: novaseqxplus-25b"
    )


def test_v3_load_analysis_with_undefined_bi_process() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "multi"
        / "analysis_with_undefined_bi_process.yml"
    )

    with pytest.raises(SystemExit) as exc_info:
        make_import_bundle_from_files([f], check=True)

    assert (
        exc_info.value.code
        == f"Analysis at index 0 in file {f} is referencing "
        f"an undefined bi process: varscope-3"
    )


def test_v3_load_analysis_from_multiple_files() -> None:
    filepaths = [
        RES_DIR / "import_bundles" / "v3_analyses.yml",
        RES_DIR / "import_bundles" / "v3_two_analyses_in_two_documents.yml",
    ]
    bdl = make_import_bundle_from_files(filepaths)
    assert bdl.get_nb_files("vcf") == 3
    assert bdl.analyses.get_nb_files() == 3
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_load_analysis_and_processes_from_multiple_files() -> None:
    filepaths = [
        RES_DIR / "import_bundles" / "v3_analyses.yml",
        RES_DIR
        / "import_bundles"
        / "multi"
        / "analysis_with_defined_bi_and_wet_processes.yml",
        RES_DIR
        / "import_bundles"
        / "wet_processes"
        / "only_mandatory_keys.yml",
        RES_DIR / "import_bundles" / "bi_processes" / "only_mandatory_keys.yml",
    ]

    bdl = make_import_bundle_from_files(filepaths)
    assert bdl.get_nb_files("vcf") == 2
    assert bdl.analyses.get_nb_files() == 2
    assert bdl.wet_processes.get_process_ids() == {
        "wgs-novaseqxplus-25b",
        "novaseqxplus-10b",
    }
    assert bdl.bi_processes.get_process_ids() == {"dragen-4123", "varscope-3"}
    assert bdl.analyses.get_all_categories() == {"vcf"}


def test_v3_custom_prefix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_custom_prefix.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.analyses.get_nb_files() == 1


def test_v3_custom_suffix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_custom_suffix.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.analyses.get_nb_files() == 1


def test_v3_custom_prefix_and_suffix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_custom_prefix_and_suffix.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.analyses.get_nb_files() == 1


def test_v3_default_prefix_and_suffix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_default_prefix_and_suffix.yml"
    bdl = make_import_bundle_from_files([f])
    assert bdl.analyses.get_nb_files() == 1


def test_v3_tags_must_be_defined_only_once() -> None:
    files = [
        RES_DIR
        / "import_bundles"
        / "tags"
        / "v3_default_prefix_and_suffix.yml",
        RES_DIR / "import_bundles" / "tags" / "v3_tags.yml",
    ]
    with pytest.raises(RuntimeError) as exc_info:
        make_import_bundle_from_files(files)
    assert exc_info.value.args[0] == (
        f"Only one 'tags' key should be defined "
        f"across all documents, "
        f"but multiple were found : {', '.join(str(f) for f in files)}"
    )


def test_v3_tags_are_applied_to_all_analyses() -> None:
    files = [
        RES_DIR / "import_bundles" / "tags" / "v3_tags.yml",
        RES_DIR / "import_bundles" / "tags" / "v3_no_tags.yml",
    ]
    bdl = make_import_bundle_from_files(files)
    assert bdl.analyses.get_nb_files() == 2


def test_v3_word_char_in_prefix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_word_char_in_prefix.yml"
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert (
        exc_info.value.args[0]
        == "Key 'prefix' should only contain one special character, "
        "excluding the following : (, ), ?, <, >."
    )


def test_v3_excluded_char_in_prefix() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_excluded_char_in_prefix.yml"
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert (
        exc_info.value.args[0]
        == "Key 'prefix' should only contain one special character, "
        "excluding the following : (, ), ?, <, >."
    )


def test_v3_more_than_one_char_in_prefix() -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "tags"
        / "v3_more_than_one_char_in_prefix.yml"
    )
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    assert (
        exc_info.value.args[0]
        == "Key 'prefix' should only contain one special character, "
        "excluding the following : (, ), ?, <, >."
    )


def test_v3_non_word_chars_in_tags() -> None:
    f = RES_DIR / "import_bundles" / "tags" / "v3_non_word_chars_in_tags.yml"
    with pytest.raises(SchemaError) as exc_info:
        make_import_bundle_from_files([f])
    # There is a bug, schema is not returning the custom error message provided in the schema.
    # It only returns the error "Wrong key".
    # See: https://github.com/keleshev/schema/issues/255
    assert "Wrong key" in exc_info.value.args[0]


def test_v3_undefined_tags_used_in_file_prefix_default_prefix(
    caplog: LogCaptureFixture,
) -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "tags"
        / "v3_undefined_tags_used_in_file_prefix_default_prefix.yml"
    )
    with caplog.at_level(logging.WARNING):
        bdl = make_import_bundle_from_files([f])
    # 'file_prefix' is wrong, so we don't expect any matched files.
    assert bdl.analyses.get_nb_files() == 0
    assert (
        "String '%a_' in key 'file_prefix' looks like an undefined tag. "
        "If this string is not a tag, you can ignore this warning."
    ) in caplog.text
    assert (
        "String '%b' in key 'file_prefix' looks like an undefined tag. "
        "If this string is not a tag, you can ignore this warning."
    ) in caplog.text


def test_v3_undefined_tags_used_in_file_prefix_custom_prefix_and_suffix(
    caplog: LogCaptureFixture,
) -> None:
    f = (
        RES_DIR
        / "import_bundles"
        / "tags"
        / "v3_undefined_tags_used_in_file_prefix_custom_prefix_and_suffix.yml"
    )
    with caplog.at_level(logging.WARNING):
        bdl = make_import_bundle_from_files([f])
    # 'file_prefix' is wrong, so we don't expect any matched files.
    assert bdl.analyses.get_nb_files() == 0
    assert (
        "String '$a$' in key 'file_prefix' looks like an undefined tag. "
        "If this string is not a tag, you can ignore this warning."
    ) in caplog.text
    assert (
        "String '$b$' in key 'file_prefix' looks like an undefined tag. "
        "If this string is not a tag, you can ignore this warning."
    ) in caplog.text
