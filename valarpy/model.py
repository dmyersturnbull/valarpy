import os as __os
from pathlib import PurePath as __PurePath
from typing import Iterable as __Iterable
from typing import Union as __Union
from typing import Optional as _Optional

import peewee
from peewee import *

from valarpy.definitions import *
from valarpy.metamodel import BaseModel, EnumField


def _blob_type_from_legacy(legacy) -> BlobType:
    return {
        "byte": BlobType.int_sbyte,
        "short": BlobType.int_sshort,
        "int": BlobType.int_sint,
        "long": BlobType.int_slong,
        "float": BlobType.int_sfloat,
        "double": BlobType.int_sdouble,
        "unsigned_byte": BlobType.int_ubyte,
        "unsigned_short": BlobType.int_ushort,
        "unsigned_int": BlobType.int_uint,
        "unsigned_long": BlobType.int_ulong,
        "unsigned_float": BlobType.int_ufloat,
        "unsigned_double": BlobType.int_udouble,
        "utf8_char": BlobType.str_utf8,
        "utf16_char": BlobType.str_utf16,
        "other": BlobType.blob
    }.get(legacy, BlobType.unknown)


class ISuppliers(Supplier, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "suppliers"


class IPlateTypes(PlateType, BaseModel):  # pragma: no cover
    n_columns = IntegerField()
    n_rows = IntegerField()
    name = CharField(null=True)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=ISuppliers, null=True)
    part_number = CharField(index=True, null=True)

    class Meta:
        table_name = "plate_types"
        indexes = ((("n_rows", "n_columns"), False),)


class IUsers(User, BaseModel):  # pragma: no cover
    @property
    def sstring(self) -> str:
        pass

    bcrypt_hash = CharField(index=True, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    first_name = CharField(index=True)
    last_name = CharField(index=True)
    username = CharField(unique=True)
    write_access = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)

    class Meta:
        table_name = "users"


class IPlates(Plate, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_plated = DateTimeField(index=True, null=True)
    person_plated = ForeignKeyField(column_name="person_plated_id", field="id", model=IUsers)
    plate_type = ForeignKeyField(
        column_name="plate_type_id", field="id", model=IPlateTypes, null=True
    )

    class Meta:
        table_name = "plates"


class IBatteries(Battery, BaseModel):  # pragma: no cover
    assays_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    author = ForeignKeyField(column_name="author_id", field="id", model=IUsers, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    length = IntegerField(index=True)
    name = CharField(unique=True)
    notes = CharField(null=True)
    # these exist, but we don't need them in valarpy
    #template = IntegerField(column_name="template_id", index=True, null=True)

    class Meta:
        table_name = "batteries"


class IProjectTypes(ProjectType, BaseModel):  # pragma: no cover
    description = TextField()
    name = CharField(unique=True)

    class Meta:
        table_name = "project_types"


class IProjects(Project, BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=IUsers)
    name = CharField(unique=True)
    description = CharField(null=True)
    type = ForeignKeyField(column_name="type_id", field="id", model=IProjectTypes, null=True)

    class Meta:
        table_name = "projects"


class IExperiments(Experiment, BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    battery = ForeignKeyField(column_name="battery_id", field="id", model=IBatteries)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=IUsers)
    default_acclimation_sec = IntegerField()
    description = CharField(null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    project = ForeignKeyField(column_name="project_id", field="id", model=IProjects)
    # these exist, but we don't need them in valarpy
    #template_plate = ForeignKeyField(
    #    column_name="template_plate_id", field="id", model=ITemplatePlates, null=True
    #)
    #transfer_plate = ForeignKeyField(
    #    column_name="transfer_plate_id", field="id", model=ITransferPlates, null=True
    #)

    class Meta:
        table_name = "experiments"


class IExperimentTags(ExperimentTag, BaseModel):  # pragma: no cover
    name = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=IExperiments)
    value = CharField()

    class Meta:
        table_name = "experiment_tags"
        indexes = ((("experiment", "name"), True),)


class ISaurons(Sauron, BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(unique=True)

    class Meta:
        table_name = "saurons"

    @property
    def is_active(self) -> bool:
        return getattr(self, "active")

    @property
    def description(self) -> str:
        return "Sauron " + self.name


class ISauronConfigs(SauronConfig, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_changed = DateTimeField()
    description = TextField()
    sauron = ForeignKeyField(column_name="sauron_id", field="id", model=ISaurons)

    class Meta:
        table_name = "sauron_configs"
        indexes = ((("sauron", "datetime_changed"), True),)


class ISubmissions(Submission, BaseModel):  # pragma: no cover
    acclimation_sec = IntegerField(null=True)
    continuing = ForeignKeyField(column_name="continuing_id", field="id", model="self", null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_dosed = DateTimeField(null=True)
    datetime_plated = DateTimeField()
    description = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=IExperiments)
    lookup_hash = CharField(unique=True)
    notes = TextField(null=True)
    person_plated = ForeignKeyField(column_name="person_plated_id", field="id", model=IUsers)
    user = ForeignKeyField(backref="users_user_set", column_name="user_id", field="id", model=IUsers)

    class Meta:
        table_name = "submissions"


class IConfigFiles(ConfigFile, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    text_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    text = TextField(column_name="toml_text")

    class Meta:
        table_name = "config_files"


class IRuns(Run, BaseModel):  # pragma: no cover
    acclimation_sec = IntegerField(index=True, null=True)
    config_file = ForeignKeyField(
        column_name="config_file_id", field="id", model=IConfigFiles, null=True
    )
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_dosed = DateTimeField(index=True, null=True)
    datetime_run = DateTimeField(index=True)
    description = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=IExperiments)
    experimentalist = ForeignKeyField(column_name="experimentalist_id", field="id", model=IUsers)
    incubation_min = IntegerField(index=True, null=True)
    name = CharField(null=True, unique=True)
    notes = TextField(null=True)
    plate = ForeignKeyField(column_name="plate_id", field="id", model=IPlates)
    sauron_config = ForeignKeyField(column_name="sauron_config_id", field="id", model=ISauronConfigs)
    submission = ForeignKeyField(
        column_name="submission_id", field="id", model=ISubmissions, null=True, unique=True
    )
    tag = CharField(constraints=[SQL("DEFAULT ''")], unique=True)

    class Meta:
        table_name = "runs"


class IAssays(Assay, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    length = IntegerField()
    name = CharField(unique=True)
    # these exist, but we don't need them in valarpy
    #template_assay = ForeignKeyField(
    #    column_name="template_assay_id", field="id", model=ITemplateAssays, null=True
    #)

    class Meta:
        table_name = "assays"
        indexes = ((("name", "frames_sha1"), True),)


class IControlTypes(ControlType, BaseModel):  # pragma: no cover
    description = CharField()
    drug_related = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)
    genetics_related = IntegerField(index=True)
    name = CharField(unique=True)
    positive = IntegerField(index=True)

    class Meta:
        table_name = "control_types"


class IGeneticVariants(GeneticVariant, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=IUsers)
    date_created = DateField(null=True)
    father = ForeignKeyField(column_name="father_id", field="id", model="self", null=True)
    fully_annotated = IntegerField(constraints=[SQL("DEFAULT 0")])
    lineage_type = EnumField(
        choices=("injection", "cross", "selection", "wild-type"), index=True, null=True
    )  # auto-corrected to Enum
    mother = ForeignKeyField(
        backref="genetic_variants_mother_set",
        column_name="mother_id",
        field="id",
        model="self",
        null=True,
    )
    name = CharField(unique=True)
    notes = TextField(null=True)

    class Meta:
        table_name = "genetic_variants"


class IWells(Well, BaseModel):  # pragma: no cover
    age = IntegerField(null=True)
    control_type = ForeignKeyField(
        column_name="control_type_id", field="id", model=IControlTypes, null=True
    )
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    n = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    run = ForeignKeyField(column_name="run_id", field="id", model=IRuns)
    variant = ForeignKeyField(
        column_name="variant_id", field="id", model=IGeneticVariants, null=True
    )
    well_group = CharField(index=True, null=True)
    well_index = IntegerField(index=True)

    class Meta:
        table_name = "wells"
        indexes = ((("run", "well_index"), True),)


class IAnnotations(RunAnnotation, BaseModel):  # pragma: no cover
    annotator = ForeignKeyField(column_name="annotator_id", field="id", model=IUsers)
    assay = ForeignKeyField(column_name="assay_id", field="id", model=IAssays, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = TextField(null=True)
    level = EnumField(
        choices=(
            "0:good",
            "1:note",
            "2:caution",
            "3:warning",
            "4:danger",
            "9:deleted",
            "to_fix",
            "fixed",
        ),
        constraints=[SQL("DEFAULT '1:note'")],
        index=True,
    )  # auto-corrected to Enum
    name = CharField(index=True, null=True)
    run = ForeignKeyField(column_name="run_id", field="id", model=IRuns, null=True)
    submission = ForeignKeyField(
        column_name="submission_id", field="id", model=ISubmissions, null=True
    )
    value = CharField(null=True)
    well = ForeignKeyField(column_name="well_id", field="id", model=IWells, null=True)

    class Meta:
        table_name = "annotations"


class IAssayPositions(AssayPosition, BaseModel):  # pragma: no cover
    assay = ForeignKeyField(column_name="assay_id", field="id", model=IAssays)
    battery = ForeignKeyField(column_name="battery_id", field="id", model=IBatteries)
    start = IntegerField(index=True)

    class Meta:
        table_name = "assay_positions"
        indexes = ((("battery", "assay", "start"), True),)


class IAudioFiles(AudioFile, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=IUsers, null=True)
    data = BlobField()  # auto-corrected to BlobField
    filename = CharField(unique=True)
    n_seconds = FloatField()
    notes = CharField(null=True)
    sha1 = BlobField(unique=True)  # auto-corrected to BlobField

    class Meta:
        table_name = "audio_files"


class ILocations(Location, BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(constraints=[SQL("DEFAULT ''")])
    name = CharField(unique=True)
    part_of = ForeignKeyField(column_name="part_of", field="id", model="self", null=True)
    purpose = CharField(constraints=[SQL("DEFAULT ''")])
    temporary = IntegerField(constraints=[SQL("DEFAULT 0")])

    @property
    def is_temporary(self) -> bool:
        return self.temporary

    class Meta:
        table_name = "locations"


class IRefs(Ref, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_downloaded = DateTimeField(null=True)
    description = CharField(null=True)
    external_version = CharField(index=True, null=True)
    name = CharField(unique=True)
    url = CharField(index=True, null=True)

    @property
    def sstring(self) -> str:
        """Short string of the ID. This can be overridden."""
        return "ref." + str(self.id)

    class Meta:
        table_name = "refs"


class ICompounds(Compound, BaseModel):  # pragma: no cover
    chembl = CharField(column_name="chembl_id", index=True, null=True)
    chemspider = IntegerField(column_name="chemspider_id", null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    inchi = CharField()
    inchikey = CharField(unique=True)
    smiles = CharField(null=True)

    @property
    def inchikey_connectivity(self) -> str:
        return self.inchikey[:14]

    @property
    def pubchem(self) -> _Optional[str]:
        return None

    @property
    def type(self) -> CompoundType:
        return CompoundType.molecule

    class Meta:
        table_name = "compounds"


class IBatches(Batch, BaseModel):  # pragma: no cover
    amount = CharField(null=True)
    box_number = IntegerField(index=True, null=True)
    compound = ForeignKeyField(column_name="compound_id", field="id", model=ICompounds, null=True)
    concentration_millimolar = FloatField(null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    date_ordered = DateField(index=True, null=True)
    legacy_internal = CharField(column_name="legacy_internal_id", index=True, null=True)
    location = ForeignKeyField(column_name="location_id", field="id", model=ILocations, null=True)
    location_note = CharField(null=True)
    lookup_hash = CharField(unique=True)
    made_from = ForeignKeyField(column_name="made_from_id", field="id", model="self", null=True)
    molecular_weight = FloatField(null=True)
    notes = TextField(null=True)
    person_ordered = ForeignKeyField(
        column_name="person_ordered", field="id", model=IUsers, null=True
    )
    ref = ForeignKeyField(column_name="ref_id", field="id", model=IRefs, null=True)
    solvent = IntegerField(column_name="solvent_id", index=True, null=True)
    # hide to make queries easier
    # solvent = ForeignKeyField(backref='compounds_solvent_set', column_name='solvent_id', field='id', model=ICompounds, null=True)
    supplier_catalog_number = CharField(null=True)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=ISuppliers, null=True)
    tag = CharField(null=True, unique=True)
    well_number = IntegerField(index=True, null=True)

    class Meta:
        table_name = "batches"
        indexes = ((("box_number", "well_number"), True),)


class IBatchLabels(BatchLabel, BaseModel):  # pragma: no cover
    batch = ForeignKeyField(column_name="batch_id", field="id", model=IBatches)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(index=True)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=IRefs)

    class Meta:
        table_name = "batch_labels"


class ISensors(Sensor, BaseModel):  # pragma: no cover
    _blob_type = EnumField(
        choices=(
            "assay_start",
            "protocol_start",
            "every_n_milliseconds",
            "every_n_frames",
            "arbitrary",
        ),
        null=True,
        column_name="blob_type"
    )  # auto-corrected to Enum
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    _data_type = EnumField(
        choices=(
            "byte",
            "short",
            "int",
            "float",
            "double",
            "unsigned_byte",
            "unsigned_short",
            "unsigned_int",
            "unsigned_float",
            "unsigned_double",
            "utf8_char",
            "long",
            "unsigned_long",
            "other",
        ),
        column_name="blob_type"
    )  # auto-corrected to Enum
    description = CharField(null=True)
    n_between = IntegerField(null=True)
    name = CharField(unique=True)

    @property
    def blob_type(self) -> BlobType:
        return _blob_type_from_legacy(self._data_type)

    @property
    def sensor_type(self) -> SensorType:
        """
        WARNING:
            This function is currently broken.
        """
        if self.name.endswith("_millis"):
            return SensorType.periodic_millis
        elif self.name.endswith("_values"):
            return SensorType.periodic_values
        # TODO temp
        raise NotImplementedError()

    class Meta:
        table_name = "sensors"


class IStimuli(Stimulus, BaseModel):  # pragma: no cover
    analog = IntegerField(constraints=[SQL("DEFAULT 0")])
    audio_file = ForeignKeyField(
        column_name="audio_file_id", field="id", model=IAudioFiles, null=True, unique=True
    )
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    default_color = CharField()
    description = CharField(null=True)
    name = CharField(unique=True)
    rgb = BlobField(null=True)  # auto-corrected to BlobField
    wavelength_nm = IntegerField(null=True)

    @property
    def sstring(self) -> str:
        """Short string of the ID. This can be overridden."""
        return "stim." + str(self.id)

    class Meta:
        table_name = "stimuli"


class ICompoundLabels(CompoundLabel, BaseModel):  # pragma: no cover
    compound = ForeignKeyField(column_name="compound_id", field="id", model=ICompounds)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField()
    ref = ForeignKeyField(column_name="ref_id", field="id", model=IRefs)

    class Meta:
        table_name = "compound_labels"


class IFeatures(Feature, BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    data_type = EnumField(
        choices=(
            "byte",
            "short",
            "int",
            "float",
            "double",
            "unsigned_byte",
            "unsigned_short",
            "unsigned_int",
            "unsigned_float",
            "unsigned_double",
            "utf8_char",
        ),
        constraints=[SQL("DEFAULT 'float'")],
    )  # auto-corrected to Enum
    description = CharField()
    dimensions = CharField()
    name = CharField(unique=True)

    @property
    def blob_type(self) -> BlobType:
        return _blob_type_from_legacy(self._data_type)

    class Meta:
        table_name = "features"


class IRois(BaseModel):  # pragma: no cover
    ref = ForeignKeyField(column_name="ref_id", field="id", model=IRefs)
    well = ForeignKeyField(column_name="well_id", field="id", model=IWells)
    x0 = IntegerField()
    x1 = IntegerField()
    y0 = IntegerField()
    y1 = IntegerField()

    @property
    def sstring(self) -> str:
        """Short string of the ID. This can be overridden."""
        return "roi." + str(self.id)

    class Meta:
        table_name = "rois"


class IRunTags(BaseModel):  # pragma: no cover
    name = CharField()
    run = ForeignKeyField(column_name="run_id", field="id", model=IRuns)
    value = CharField()

    class Meta:
        table_name = "run_tags"
        indexes = ((("run", "name"), True),)


class ISauronSettings(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(index=True)
    sauron_config = ForeignKeyField(column_name="sauron_config_id", field="id", model=ISauronConfigs)
    value = CharField()

    class Meta:
        table_name = "sauron_settings"
        indexes = ((("sauron_config", "name"), True),)


class ISensorData(BaseModel):  # pragma: no cover
    floats = BlobField()  # auto-corrected to BlobField
    floats_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    run = ForeignKeyField(column_name="run_id", field="id", model=IRuns)
    sensor = ForeignKeyField(column_name="sensor_id", field="id", model=ISensors)

    class Meta:
        table_name = "sensor_data"


class IStimulusFrames(BaseModel):  # pragma: no cover
    assay = ForeignKeyField(column_name="assay_id", field="id", model=IAssays)
    frames = BlobField()  # auto-corrected to BlobField
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    stimulus = ForeignKeyField(column_name="stimulus_id", field="id", model=IStimuli)

    class Meta:
        table_name = "stimulus_frames"
        indexes = ((("assay", "stimulus"), True),)


class ISubmissionParams(BaseModel):  # pragma: no cover
    name = CharField()
    param_type = EnumField(
        choices=("n_fish", "compound", "dose", "variant", "dpf", "group")
    )  # auto-corrected to Enum
    submission = ForeignKeyField(column_name="submission_id", field="id", model=ISubmissions)
    value = CharField()

    class Meta:
        table_name = "submission_params"
        indexes = ((("submission", "name"), True),)


class ISubmissionRecords(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_modified = DateTimeField()
    sauron = ForeignKeyField(column_name="sauron_id", field="id", model=ISaurons)
    status = CharField(index=True)
    submission = ForeignKeyField(column_name="submission_id", field="id", model=ISubmissions)

    class Meta:
        table_name = "submission_records"
        indexes = ((("submission", "status", "datetime_modified"), True),)


class IWellFeatures(BaseModel):  # pragma: no cover
    floats = BlobField()  # auto-corrected to BlobField
    sha1 = BlobField(index=True)  # auto-corrected to BlobField
    type = ForeignKeyField(column_name="type_id", field="id", model=IFeatures)
    well = ForeignKeyField(column_name="well_id", field="id", model=IWells)

    class Meta:
        table_name = "well_features"


class IWellTreatments(BaseModel):  # pragma: no cover
    batch = ForeignKeyField(column_name="batch_id", field="id", model=IBatches)
    micromolar_dose = FloatField(null=True)
    well = ForeignKeyField(column_name="well_id", field="id", model=IWells)

    class Meta:
        table_name = "well_treatments"
        indexes = ((("well", "batch"), True),)


class IBatchAnnotations(BaseModel):  # pragma: no cover
    annotator = ForeignKeyField(column_name="annotator_id", field="id", model=IUsers)
    batch = ForeignKeyField(column_name="batch_id", field="id", model=IBatches, null=False)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = TextField(null=True)
    level = EnumField(
        choices=("0:good", "1:note", "2:caution", "3:warning", "4:danger", "9:deleted"),
        constraints=[SQL("DEFAULT '1:note'")],
        index=True,
    )  # auto-corrected to Enum
    name = CharField(index=True, null=True)
    value = CharField(null=True)

    class Meta:
        table_name = "batch_annotations"


ExpressionLike = peewee.ColumnBase
ExpressionsLike = __Union[ExpressionLike, __Iterable[ExpressionLike]]
PathLike = __Union[str, __PurePath, __os.PathLike]
