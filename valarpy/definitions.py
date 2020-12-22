from __future__ import annotations
from datetime import datetime as _datetime
from datetime import date as _date
import enum as _enum
from typing import Optional as _Optional
from typing import Sequence as _Sequence
from typing import Union as _Union


class _ABC:
    """
    Fake Abstract Base Class (ABC) because peewee Model supplies its own metaclass,
    so there's a metaclass conflict if we specify metaclass=ABCMeta or inherit from ABC.
    """


class BlobType(_enum.Enum):
    int_sbyte = _enum.auto()
    int_ubyte = _enum.auto()
    int_sshort = _enum.auto()
    int_ushort = _enum.auto()
    int_sint = _enum.auto()
    int_uint = _enum.auto()
    int_slong = _enum.auto()
    int_ulong = _enum.auto()
    int_slonglong = _enum.auto()
    int_ulonglong = _enum.auto()
    float_sfloat = _enum.auto()
    float_ufloat = _enum.auto()
    float_sdouble = _enum.auto()
    float_udouble = _enum.auto()
    float_sdoubledouble = _enum.auto()
    float_udoubledouble = _enum.auto()
    img_png = _enum.auto()
    img_jpg = _enum.auto()
    img_webp = _enum.auto()
    img_tiff = _enum.auto()
    img_heif = _enum.auto()
    img_other = _enum.auto()
    audio_wav = _enum.auto()
    audio_flac = _enum.auto()
    audio_other = _enum.auto()
    video_hevc_mkv = _enum.auto()
    video_av1_mkv = _enum.auto()
    video_vvc_mkv = _enum.auto()
    video_other_mkv = _enum.auto()
    video_other = _enum.auto()
    str_utf8 = _enum.auto()
    str_utf16 = _enum.auto()
    blob = _enum.auto()
    unknown = _enum.auto()

    @property
    def is_floating_point(self) -> bool:
        return self.name.startswith("float_")

    @property
    def is_integer(self) -> bool:
        return self.name.startswith("int_")

    @property
    def is_image(self) -> bool:
        return self.name.startswith("img")

    @property
    def is_audio(self) -> bool:
        return self.name.startswith("audio_")

    @property
    def is_video(self) -> bool:
        return self.name.startswith("video_")

    @property
    def is_signed(self) -> bool:
        if not self.is_integer and not self.is_floating_point:
            # this is a dangerous use, so let's be explicit
            # an alternative is to also define an `is_unsigned`
            raise ValueError(f"Can't determine whether {self.name} is signed or unsigned")
        return self in {BlobType.sbyte, BlobType.sshort, BlobType.sint, BlobType.slong, BlobType.sfloat, BlobType.sdouble}


class SensorType(_enum.Enum):
    periodic_values = _enum.auto()
    periodic_millis = _enum.auto()
    periodic_ids = _enum.auto()
    image = _enum.auto()
    audio = _enum.auto()
    blob = _enum.auto()


class AnnotationLevel(_enum.Enum):
    good = 0
    note = 1
    caution = 2
    warning = 3
    danger = 4
    deleted = 5
    to_fix = 111
    fixed = -111

    def __lt__(self, other):
        if not isinstance(other, AnnotationLevel):
            raise TypeError(f"Cannot compare {other} of type {type(other)}")
        # it's too weird to put this in the enum values,
        # but "fixed" isn't actually better than "good"
        # if we have to make a decision, it's probably between "note" and "caution"
        # if we put it as 1.5, then it would often get counted by mistake
        # because 1:note is a good cutoff for "bad from now on"
        # noinspection PyTypeChecker
        fixmap = {e: 0.5 if e==AnnotationLevel.fixed else e.value for e in self}
        return fixmap[self] < fixmap[other]

    @property
    def is_bad(self) -> bool:
        return self in {AnnotationLevel.caution, AnnotationLevel.warning, AnnotationLevel.danger}


class CompoundType(_enum.Enum):
    molecule = _enum.auto()  # inc. ions
    peptide = _enum.auto()
    nucleic = _enum.auto()
    mixture = _enum.auto()
    blinded = _enum.auto()
    other = _enum.auto()


class _Fetchable(_ABC):
    @classmethod
    def fetch(cls):
        raise NotImplementedError()

    @classmethod
    def fetch_or_none(cls):
        raise NotImplementedError()

    @classmethod
    def fetch_all(cls):
        raise NotImplementedError()

    @classmethod
    def fetch_all_or_none(cls):
        raise NotImplementedError()


class Row(_Fetchable, _ABC):
    @property
    def id(self) -> int:
        return getattr(self, "id")

    @property
    def sstring(self) -> str:
        raise NotImplementedError()


class _TimestampedRow(Row, _ABC):
    @property
    def created(self) -> _datetime:
        return getattr(self, "created")


class _NameValueRow(_TimestampedRow, _ABC):
    @property
    def name(self) -> str:
        return getattr(self, "name")

    @property
    def value(self) -> str:
        return getattr(self, "value")


class _DescribedRow(_TimestampedRow, _ABC):
    @property
    def name(self) -> str:
        return getattr(self, "name")

    @property
    def description(self) -> str:
        return getattr(self, "description")


class Supplier(_DescribedRow, _ABC):
    pass

class Ref(_DescribedRow, _ABC):
    pass

class Sauron(_DescribedRow, _ABC):

    @property
    def is_active(self) -> bool:
        return getattr(self, "is_active")


class SauronConfig(_TimestampedRow, _ABC):

    @property
    def sauron(self) -> Sauron:
        return getattr(self, "sauron")

    @property
    def description(self) -> str:
        return getattr(self, "description")

    @property
    def datetime_changed(self) -> _datetime:
        return getattr(self, "datetime_changed")


class ProjectType(_DescribedRow, _ABC):
    """

    """


class Project(_DescribedRow, _ABC):
    @property
    def type(self) -> ProjectType:
        return getattr(self, "type")

    @property
    def active(self) -> bool:
        return getattr(self, "active")

    @property
    def creator(self) -> User:
        return getattr(self, "creator")

    @property
    def notes(self) -> str:
        return getattr(self, "notes")


class Experiment(_DescribedRow, _ABC):
    @property
    def project(self) -> Project:
        return getattr(self, "project")

    @property
    def default_acclimation_sec(self) -> int:
        return getattr(self, "default_acclimation_sec")

    @property
    def battery(self) -> Battery:
        return getattr(self, "battery")

    @property
    def active(self) -> bool:
        return getattr(self, "active")

    @property
    def creator(self) -> User:
        return getattr(self, "creator")

    @property
    def notes(self) -> str:
        return getattr(self, "notes")


class User(Row, _ABC):
    @property
    def username(self):
        return getattr(self, "username")

    @property
    def first_name(self) -> str:
        return getattr(self, "first_name")

    @property
    def last_name(self) -> str:
        return getattr(self, "last_name")

    @property
    def has_write_access(self) -> str:
        return getattr(self, "write_access")


class PlateType(Row, _ABC):

    @property
    def n_rows(self) -> int:
        return getattr(self, "n_rows")

    @property
    def n_columns(self) -> int:
        return getattr(self, "n_columns")


class Plate(_TimestampedRow, _ABC):
    @property
    def datetime_plated(self) -> _datetime:
        return getattr(self, "datetime_plated")

    @property
    def type(self) -> PlateType:
        return getattr(self, "plate_type")


class Submission(_TimestampedRow, _ABC):

    @property
    def datetime_dosed(self) -> _Optional[_datetime]:
        return getattr(self, "datetime_dosed")

    @property
    def experimentalist(self) -> User:
        return getattr(self, "experimentalist")


class Run(_DescribedRow, _ABC):

    @property
    def tag(self) -> str:
        return getattr(self, "tag")

    @property
    def plate(self) -> int:
        return getattr(self, "plate")

    @property
    def submission(self) -> _Optional[Submission]:
        return getattr(self, "submission")

    @property
    def experiment(self) -> Experiment:
        return getattr(self, "experiment")

    @property
    def sauron_config(self) -> SauronConfig:
        return getattr(self, "sauron_config")

    @property
    def experimentalist(self) -> User:
        return getattr(self, "experimentalist")

    @property
    def datetime_run(self) -> _datetime:
        return getattr(self, "datetime_run")

    @property
    def datetime_dosed(self) -> _Optional[_datetime]:
        return getattr(self, "datetime_dosed")

    @property
    def incubation_minutes(self) -> int:
        return getattr(self, "incubation_minutes")

    @property
    def notes(self) -> _Optional[str]:
        return getattr(self, "notes")


class ConfigFile(_TimestampedRow, _ABC):

    @property
    def text(self) -> int:
        return getattr(self, "text")

    @property
    def run(self) -> Run:
        return getattr(self, "run")


class ControlType(Row, _ABC):

    @property
    def positive(self) -> bool:
        return getattr(self, "positive")

    @property
    def drug_related(self) -> bool:
        return getattr(self, "drug_related")

    @property
    def genetics_related(self) -> bool:
        return getattr(self, "genetics_related")


class GeneticVariant(_DescribedRow, _ABC):

    @property
    def creator(self) -> User:
        return getattr(self, "creator")

    @property
    def date_created(self) -> _date:
        return getattr(self, "date_created")


class Well(Row, _ABC):

    @property
    def index(self) -> int:
        return self.well_index

    @property
    def well_index(self) -> int:
        return getattr(self, "well_index")

    @property
    def group(self) -> _Optional[str]:
        return self.well_group

    @property
    def well_group(self) -> _Optional[str]:
        return getattr(self, "well_group")

    @property
    def age(self) -> int:
        return getattr(self, "age")

    @property
    def n(self) -> int:
        return getattr(self, "n")

    @property
    def run(self) -> Run:
        return getattr(self, "run")

    @property
    def variant(self) -> GeneticVariant:
        return getattr(self, "variant")

    @property
    def control_type(self) -> _Optional[ControlType]:
        return getattr(self, "control_type")


class Compound(_TimestampedRow, _ABC):

    @property
    def inchi(self) -> _Optional[str]:
        return getattr(self, "inchi")

    @property
    def inchikey(self) -> _Optional[str]:
        return getattr(self, "inchikey")

    @property
    def inchikey_connectivity(self) -> _Optional[str]:
        return getattr(self, "inchikey")

    @property
    def smiles(self) -> _Optional[str]:
        return getattr(self, "smiles")

    @property
    def chembl(self) -> _Optional[str]:
        return getattr(self, "chembl")

    @property
    def pubchem(self) -> _Optional[str]:
        return getattr(self, "pubchem")

    @property
    def chemspider(self) -> _Optional[str]:
        return getattr(self, "chemspider")

    @property
    def type(self) -> CompoundType:
        return getattr(self, "type")


class Location(_DescribedRow, _ABC):

    @property
    def is_temporary(self) -> bool:
        return getattr(self, "is_temporary")



class Batch(_DescribedRow, _ABC):

    @property
    def lookup_hash(self) -> str:
        return getattr(self, "lookup_hash")

    @property
    def tag(self) -> _Optional[str]:
        return getattr(self, "tag")

    @property
    def compound(self) -> _Optional[Compound]:
        return getattr(self, "compound")

    @property
    def ref(self) -> Ref:
        return getattr(self, "ref")

    @property
    def supplier(self) -> Supplier:
        return getattr(self, "supplier")

    @property
    def supplier_catalog_number(self) -> _Optional[str]:
        return getattr(self, "supplier_catalog_number")

    @property
    def made_from(self) -> _Optional[Batch]:
        return getattr(self, "made_from")

    @property
    def solvent(self) -> _Optional[Compound]:
        return getattr(self, "solvent")

    @property
    def person_ordered(self) -> _Optional[User]:
        return getattr(self, "person_ordered")

    @property
    def amount(self) -> _Optional[str]:
        return getattr(self, "amount")

    @property
    def date_ordered(self) -> _Optional[_date]:
        return getattr(self, "date_ordered")

    @property
    def legacy_internal(self) -> _Optional[str]:
        return getattr(self, "legacy_internal")

    @property
    def location(self) -> _Optional[Location]:
        return getattr(self, "location")

    @property
    def location_note(self) -> _Optional[str]:
        return getattr(self, "location_note")

    @property
    def box_number(self) -> _Optional[int]:
        return getattr(self, "box_number")

    @property
    def well_number(self) -> _Optional[int]:
        return getattr(self, "well_number")


class Battery(_DescribedRow, _ABC):

    @property
    def length(self) -> int:
        return getattr(self, "length")

    @property
    def author(self) -> User:
        return getattr(self, "author")

    @property
    def notes(self) -> str:
        return getattr(self, "notes")


class Assay(_DescribedRow, _ABC):

    @property
    def length(self) -> int:
        return getattr(self, "length")


class AssayPosition(Row, _ABC):

    @property
    def assay(self) -> Assay:
        return getattr(self, "assay")

    @property
    def battery(self) -> Battery:
        return getattr(self, "battery")

    @property
    def start(self) -> int:
        return getattr(self, "start")


class Stimulus(_DescribedRow, _ABC):

    @property
    def default_color(self) -> str:
        return getattr(self, "default_color")

    @property
    def audio_file(self) -> _Optional[AudioFile]:
        return getattr(self, "audio_file")


class AudioFile(_TimestampedRow, _ABC):

    @property
    def filename(self) -> str:
        return getattr(self, "filename")

    @property
    def n_seconds(self) -> float:
        return getattr(self, "n_seconds")

    @property
    def data(self) -> _Optional[bytes]:
        return getattr(self, "audio_file")


class ExperimentTag(_NameValueRow, _ABC):

    @property
    def experiment(self) -> str:
        return getattr(self, "experiment")


class RunAnnotation(_NameValueRow, _ABC):

    @property
    def annotator(self) -> User:
        return getattr(self, "annotator")

    @property
    def description(self) -> str:
        return getattr(self, "description")

    @property
    def level(self) -> str:
        return getattr(self, "level")

    @property
    def run(self) -> Run:
        return getattr(self, "run")

    @property
    def submission(self) -> _Optional[Submission]:
        return getattr(self, "submission")


class RunTag(_NameValueRow, _ABC):

    @property
    def run(self) -> Run:
        return getattr(self, "run")


class Roi(Row, _ABC):

    @property
    def well(self) -> Well:
        return getattr(self, "well")

    @property
    def ref(self) -> Ref:
        return getattr(self, "ref")

    @property
    def x0(self) -> int:
        return getattr(self, "x0")

    @property
    def x1(self) -> int:
        return getattr(self, "x1")

    @property
    def y0(self) -> int:
        return getattr(self, "y0")

    @property
    def y1(self) -> int:
        return getattr(self, "y1")


class Sensor(_DescribedRow, _ABC):

    @property
    def sensor_type(self) -> SensorType:
        return getattr(self, "sensor_type")

    @property
    def blob_type(self) -> BlobType:
        return getattr(self, "blob_type")


class Feature(_DescribedRow, _ABC):

    @property
    def is_time_dependent(self) -> BlobType:
        return getattr(self, "is_time_dependent")

    def get_dimensionality(self, n_frames: int) -> _Sequence[int]:
        raise NotImplementedError()

    @property
    def blob_type(self) -> BlobType:
        return getattr(self, "blob_type")


class WellTreatment(Row, _ABC):

    @property
    def well(self) -> Well:
        return getattr(self, "well")

    @property
    def batch(self) -> Batch:
        return getattr(self, "well")

    @property
    def amount(self) -> float:
        return getattr(self, "amount")


class WellFeature(Row, _ABC):

    @property
    def feature(self) -> Feature:
        return getattr(self, "feature")

    @property
    def blob(self) -> bytes:
        return getattr(self, "blob")


class BatchAnnotation(_NameValueRow, _ABC):

    @property
    def level(self) -> AnnotationLevel:
        return getattr(self, "level")

    @property
    def description(self) -> str:
        return getattr(self, "description")

    @property
    def batch(self) -> Batch:
        return getattr(self, "batch")


class CompoundLabel(Row, _ABC):

    @property
    def compound(self) -> Compound:
        return getattr(self, "compound")

    @property
    def name(self) -> str:
        return getattr(self, "str")

    @property
    def ref(self) -> Ref:
        return getattr(self, "ref")


class BatchLabel(Row, _ABC):

    @property
    def batch(self) -> Compound:
        return getattr(self, "batch")

    @property
    def name(self) -> str:
        return getattr(self, "str")

    @property
    def ref(self) -> Ref:
        return getattr(self, "ref")


ProjectTypeLike = _Union[int, str, ProjectType]
ProjectLike = _Union[int, str, Project]
ExperimentLike = _Union[int, str, Experiment]
ExperimentTagLike = _Union[int, str, ExperimentTag]
RunAnnotationLike = _Union[int, str, RunAnnotation]
RunTagLike = _Union[int, str, RunTag]
RunLike = _Union[int, str, Run]
ControlTypeLike = _Union[int, str, ControlType]
SubmissionLike = _Union[int, str, Submission]
RoiLike = _Union[int, Roi]
SauronLike = _Union[int, str, Sauron]
SauronConfigLike = _Union[int, SauronConfig]
BatteryLike = _Union[int, str, Battery]
AssayLike = _Union[int, str, Assay]
UserLike = _Union[int, str, User]
RefLike = _Union[int, str, Ref]
SupplierLike = _Union[int, str, Supplier]
BatchLike = _Union[int, str, Batch]
CompoundLike = _Union[int, str, Compound]
SensorLike = _Union[int, str, Sensor]
StimulusLike = _Union[Stimulus, int, str]
AudioFileLike = _Union[AudioFile, int, str]
PlateTypeLike = _Union[PlateType, int, str]
GeneticVariantLike = _Union[GeneticVariant, int, str]
LocationLike = _Union[Location, int, str]
ConfigFileLike = _Union[ConfigFile, int]
WellLike = _Union[Well, int]
WellTreatmentLike = _Union[WellTreatment, int]
FeatureLike = _Union[Feature, int, str]
WellFeatureLike = _Union[Feature, int]
