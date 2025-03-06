import csv
import typing
from pathlib import Path

import pytest
import vcf
import yaml
from biophony import MutSimParams

if typing.TYPE_CHECKING:
    from genelastic.common import RandomBiProcessData

from genelastic.import_data import (
    RandomBiProcess,
    RandomBundle,
    RandomWetProcess,
)


def test_generate_random_wet_proc_same_seed() -> None:
    wet_processes = [RandomWetProcess(seed=1).to_dict() for _ in range(10)]
    assert all(wet_process == wet_processes[0] for wet_process in wet_processes)


def test_generate_random_wet_proc_different_seeds() -> None:
    wet_process1 = RandomWetProcess(seed=1).to_dict()
    wet_process2 = RandomWetProcess(seed=2).to_dict()
    assert wet_process1 != wet_process2


def test_generate_random_bi_proc_same_seed() -> None:
    bi_processes = [RandomBiProcess(seed=1).to_dict() for _ in range(10)]
    assert all(bi_process == bi_processes[0] for bi_process in bi_processes)


def test_generate_random_bi_proc_different_seeds() -> None:
    bi_process1 = RandomBiProcess(seed=1).to_dict()
    bi_process2 = RandomBiProcess(seed=2).to_dict()
    assert bi_process1 != bi_process2


def test_random_bi_process_generate_version() -> None:
    random_version_1 = RandomBiProcess._generate_version(1).split(".")
    random_version_2 = RandomBiProcess._generate_version(4).split(".")

    assert len(random_version_1) == 1
    assert len(random_version_2) == 4

    # Ensure that all numbers are integers.
    for num in random_version_1 + random_version_2:
        try:
            int(num)
        except ValueError as e:
            pytest.fail(str(e))


def test_random_bi_process_generate_version_zero_count() -> None:
    with pytest.raises(
        ValueError,
        match="Count of numbers present in the version string must be > 0.",
    ):
        RandomBiProcess._generate_version(0)


def test_random_bi_process_generate_version_negative_count() -> None:
    with pytest.raises(
        ValueError,
        match="Count of numbers present in the version string must be > 0.",
    ):
        RandomBiProcess._generate_version(-1)


def test_random_bundle(tmp_path: Path) -> None:
    analyses_count = 2
    processes_count = 2
    nb_chrom = 5
    seq_len = 1000

    bundle = RandomBundle(
        tmp_path,
        analyses_count,
        processes_count,
        nb_chrom,
        seq_len,
        MutSimParams(ins_rate=0.5),
        do_gen_coverage=False,
    )

    # Ensure generated VCF files conform to the input parameters.
    vcf_files = list(tmp_path.glob("*.vcf"))
    assert len(vcf_files) == analyses_count

    for vcf_file in vcf_files:
        vcf_content = vcf.Reader(filename=str(vcf_file))
        assert len(vcf_content.contigs) == nb_chrom

        for contig in vcf_content.contigs.values():
            assert contig.length == seq_len

    # Ensure that the generated bundle contains the correct amount of analyses and processes.
    bundle_path = tmp_path / "bundle.yml"
    bundle.to_yaml(bundle_path)

    with bundle_path.open(encoding="utf-8") as f:
        bundle_content = yaml.safe_load(f)
        assert len(bundle_content["analyses"]) == analyses_count
        assert len(bundle_content["bi_processes"]) == processes_count
        assert len(bundle_content["wet_processes"]) == processes_count


def test_random_bundle_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    analyses_count = 2
    processes_count = 2
    nb_chrom = 5
    seq_len = 1000

    bundle = RandomBundle(
        tmp_path,
        analyses_count,
        processes_count,
        nb_chrom,
        seq_len,
        MutSimParams(ins_rate=0.5),
        do_gen_coverage=False,
    )

    # Ensure generated VCF files conform to the input parameters.
    vcf_files: list[Path] = list(tmp_path.glob("*.vcf"))
    assert len(vcf_files) == analyses_count

    for vcf_file in vcf_files:
        vcf_content = vcf.Reader(filename=str(vcf_file))

        assert len(vcf_content.contigs) == nb_chrom
        for contig in vcf_content.contigs.values():
            assert contig.length == seq_len

    # Ensure that the generated bundle contains the correct amount of analyses and processes.
    bundle.to_yaml(None)
    bundle_content = yaml.safe_load(capsys.readouterr().out)
    assert len(bundle_content["analyses"]) == analyses_count
    assert len(bundle_content["bi_processes"]) == processes_count
    assert len(bundle_content["wet_processes"]) == processes_count


def test_random_bundle_with_cov(tmp_path: Path) -> None:
    analyses_count = 2
    processes_count = 2
    nb_chrom = 5
    seq_len = 1000

    bundle = RandomBundle(
        tmp_path,
        analyses_count,
        processes_count,
        nb_chrom,
        seq_len,
        MutSimParams(ins_rate=0.5),
        do_gen_coverage=True,
    )

    # Ensure generated VCF files conform to the input parameters.
    vcf_files: list[Path] = list(tmp_path.glob("*.vcf"))
    assert len(vcf_files) == analyses_count

    for vcf_file in vcf_files:
        vcf_content = vcf.Reader(filename=str(vcf_file))

        assert len(vcf_content.contigs) == nb_chrom
        for contig in vcf_content.contigs.values():
            assert contig.length == seq_len

    # Check generated coverage files.
    cov_files: list[Path] = list(tmp_path.glob("*.cov.tsv"))
    assert len(cov_files) == analyses_count

    for cov_file in cov_files:
        with cov_file.open(encoding="utf-8") as f:
            chromosomes = set()
            rd = csv.reader(f, delimiter="\t", quotechar='"')

            for row in rd:
                chromosomes.add(row[0])

            assert len(chromosomes) == nb_chrom

    # Ensure that the generated bundle contains the correct amount of analyses and processes.
    bundle_path = tmp_path / "bundle.yml"
    bundle.to_yaml(bundle_path)

    with bundle_path.open(encoding="utf-8") as f:
        bundle_content = yaml.safe_load(f)
        assert len(bundle_content["analyses"]) == analyses_count
        assert len(bundle_content["bi_processes"]) == processes_count
        assert len(bundle_content["wet_processes"]) == processes_count


def test_random_bundle_assign_process_less_processes() -> None:
    analyses_count = 4
    bi_processes = [RandomBiProcess().to_dict() for _ in range(2)]

    assigned_bi_processes = RandomBundle._assign_processes(
        bi_processes, analyses_count
    )
    assert len(assigned_bi_processes) == analyses_count


def test_random_bundle_assign_process_more_processes() -> None:
    analyses_count = 4
    bi_processes = [RandomBiProcess().to_dict() for _ in range(6)]

    assigned_bi_processes = RandomBundle._assign_processes(
        bi_processes, analyses_count
    )
    assert len(assigned_bi_processes) == analyses_count


def test_random_bundle_assign_process_equal_processes() -> None:
    analyses_count = 4
    bi_processes = [RandomBiProcess().to_dict() for _ in range(4)]

    assigned_bi_processes = RandomBundle._assign_processes(
        bi_processes, analyses_count
    )
    assert len(assigned_bi_processes) == analyses_count
    assert assigned_bi_processes == bi_processes


def test_random_bundle_assign_process_empty_processes() -> None:
    analyses_count = 4
    bi_processes: list[RandomBiProcessData] = []

    with pytest.raises(ValueError, match="Random processes list is empty."):
        RandomBundle._assign_processes(bi_processes, analyses_count)
