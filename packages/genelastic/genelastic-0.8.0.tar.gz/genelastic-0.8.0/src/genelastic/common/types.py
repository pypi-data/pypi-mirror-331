import typing

# Types related to Elasticsearch data import.
Bucket: typing.TypeAlias = dict[str, dict[typing.Any, typing.Any]]
BundleDict: typing.TypeAlias = dict[str, typing.Any]

AnalysisMetaData: typing.TypeAlias = dict[str, str | int]
WetProcessesData: typing.TypeAlias = dict[str, str | int | float]
BioInfoProcessData: typing.TypeAlias = dict[str, str | list[str]]

AnalysisDocument: typing.TypeAlias = dict[str, str | None | AnalysisMetaData]
MetadataDocument: typing.TypeAlias = dict[
    str, int | str | list[typing.Any | None]
]
ProcessDocument: typing.TypeAlias = (
    dict[str, str] | WetProcessesData | BioInfoProcessData
)
BulkItems: typing.TypeAlias = list[
    dict[str, str | MetadataDocument | AnalysisDocument | ProcessDocument]
]

# Types related to random bundle generation.
RandomBiProcessData: typing.TypeAlias = dict[str, str | list[dict[str, str]]]
RandomWetProcessData: typing.TypeAlias = dict[str, str | float]
RandomAnalysisData: typing.TypeAlias = dict[str, str | list[int | str]]
