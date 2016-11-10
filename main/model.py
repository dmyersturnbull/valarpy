from peewee import *

from db import config

database = MySQLDatabase(config['db'], **{'user': config['user'], 'password': config['password'], 'host': config['host'], 'port': config['port']})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Assays(BaseModel):
    color = CharField()
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(index=True)
    sha1_of_concatetated_frame_sha1s = CharField(index=True)

    class Meta:
        db_table = 'assays'
        indexes = (
            (('name', 'sha1_of_concatetated_frame_sha1s'), True),
        )

class Users(BaseModel):
    created = DateTimeField()
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)

    class Meta:
        db_table = 'users'

class AudioFiles(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    filename = CharField(unique=True)
    mp3 = TextField()
    n_seconds = FloatField()
    notes = CharField(null=True)
    sha1 = CharField(unique=True)

    class Meta:
        db_table = 'audio_files'

class StimulusSources(BaseModel):
    audio_file = ForeignKeyField(db_column='audio_file_id', null=True, rel_model=AudioFiles, to_field='id', unique=True)
    created = DateTimeField()
    default_color = CharField(unique=True)
    description = CharField(null=True)
    name = CharField(unique=True)
    rgb = CharField(null=True)
    wavelength_nanometers = IntegerField(null=True)

    class Meta:
        db_table = 'stimulus_sources'

class AssayFrames(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    frames = TextField()
    frames_sha1 = CharField(index=True)
    legacy_framerate_hertz = IntegerField()
    stimulus_source = ForeignKeyField(db_column='stimulus_source_id', rel_model=StimulusSources, to_field='id')

    class Meta:
        db_table = 'assay_frames'
        indexes = (
            (('assay', 'stimulus_source'), True),
        )

class Protocols(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    description = CharField(null=True)
    name = CharField(null=True, unique=True)
    notes = CharField(null=True)
    sha1_of_assay_sha1s = CharField()

    class Meta:
        db_table = 'protocols'

class AssaysInProtocols(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Protocols, to_field='id')
    start = IntegerField()

    class Meta:
        db_table = 'assays_in_protocols'
        indexes = (
            (('protocol', 'assay'), True),
        )

class CompoundSources(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'compound_sources'

class Batches(BaseModel):
    compound_source = ForeignKeyField(db_column='compound_source_id', rel_model=CompoundSources, to_field='id')
    created = DateTimeField()
    date_ordered = DateField(null=True)
    reason_ordered = CharField(null=True)
    user_ordered = ForeignKeyField(db_column='user_ordered_id', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'batches'
        indexes = (
            (('compound_source', 'date_ordered'), True),
        )

class BindingModes(BaseModel):
    created = DateTimeField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'binding_modes'

class Cameras(BaseModel):
    connection_type = CharField(null=True)
    created = DateTimeField(null=True)
    description = TextField(null=True)
    name = CharField(unique=True)
    serial_number = IntegerField(null=True)

    class Meta:
        db_table = 'cameras'

class CameraConfigurations(BaseModel):
    brightness = FloatField(null=True)
    camera = ForeignKeyField(db_column='camera_id', rel_model=Cameras, to_field='id')
    contrast = FloatField(null=True)
    created = DateTimeField()
    exposure = FloatField(null=True)
    frames_per_second = IntegerField(null=True)
    gain = FloatField(null=True)
    horizontal_pixels = IntegerField(null=True)
    hue = FloatField(null=True)
    mode = IntegerField(null=True)
    saturation = FloatField(null=True)
    startup_wait_seconds = FloatField(null=True)
    vertical_pixels = IntegerField(null=True)

    class Meta:
        db_table = 'camera_configurations'

class Compounds(BaseModel):
    chembl = CharField(db_column='chembl_id', null=True, unique=True)
    chemspider = IntegerField(db_column='chemspider_id', null=True)
    created = DateTimeField()
    inchi = CharField(null=True)
    inchikey = CharField(unique=True)
    inchikey_connectivity = CharField(index=True)
    name = CharField(index=True, null=True)
    smiles = CharField(null=True)
    special_type = CharField(null=True)

    class Meta:
        db_table = 'compounds'

class CompoundSynonyms(BaseModel):
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    name = CharField(unique=True)

    class Meta:
        db_table = 'compound_synonyms'
        indexes = (
            (('compound', 'name'), True),
        )

class DataSources(BaseModel):
    created = DateTimeField()
    date_time_downloaded = DateTimeField(null=True)
    description = CharField(null=True)
    external_version = CharField(null=True)
    name = CharField(unique=True)
    url = CharField(null=True)

    class Meta:
        db_table = 'data_sources'
        indexes = (
            (('name', 'external_version'), False),
        )

class Experiments(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Protocols, to_field='id')
    user = ForeignKeyField(db_column='user_id', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'experiments'

class FeatureTypes(BaseModel):
    created = DateTimeField()
    description = CharField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'feature_types'

class OrderedCompounds(BaseModel):
    batch = ForeignKeyField(db_column='batch_id', null=True, rel_model=Batches, to_field='id')
    box_number = IntegerField(null=True)
    compound = ForeignKeyField(db_column='compound_id', null=True, rel_model=Compounds, to_field='id')
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', null=True, rel_model=DataSources, to_field='id')
    external = CharField(db_column='external_id', null=True)
    legacy_internal = CharField(db_column='legacy_internal_id', index=True, null=True)
    mechanism_target_notes = TextField(null=True)
    millimolar_concentration = FloatField(null=True)
    molecular_weight = FloatField(null=True)
    name = CharField(null=True)
    notes = TextField(null=True)
    powder_location = TextField(null=True)
    reason_ordered = TextField(null=True)
    solvent = ForeignKeyField(db_column='solvent_id', null=True, rel_model=Compounds, related_name='compounds_solvent_set', to_field='id')
    solvent_notes = TextField(null=True)
    special_type = CharField(null=True)
    suspicious = IntegerField()
    well_number = IntegerField(null=True)

    class Meta:
        db_table = 'ordered_compounds'
        indexes = (
            (('box_number', 'well_number'), True),
            (('compound', 'batch'), False),
        )

class PlateLayouts(BaseModel):
    author = ForeignKeyField(db_column='author_id', null=True, rel_model=Users, to_field='id')
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'plate_layouts'

class Plates(BaseModel):
    created = DateTimeField()
    datetime_fish_added = DateTimeField(null=True)
    experiment = ForeignKeyField(db_column='experiment_id', rel_model=Experiments, to_field='id')

    class Meta:
        db_table = 'plates'

class Saurons(BaseModel):
    created = DateTimeField()
    number = IntegerField()

    class Meta:
        db_table = 'saurons'

class SauronConfigurations(BaseModel):
    camera_configuration = ForeignKeyField(db_column='camera_configuration_id', null=True, rel_model=CameraConfigurations, to_field='id')
    created = DateTimeField()
    description = TextField()
    sauron = ForeignKeyField(db_column='sauron_id', rel_model=Saurons, to_field='id')

    class Meta:
        db_table = 'sauron_configurations'

class PlateRuns(BaseModel):
    created = DateTimeField()
    dark_adaptation_time_seconds = IntegerField(null=True)
    datetime_dosed = DateTimeField(null=True)
    datetime_run = DateTimeField(null=True)
    days_post_fertilization = IntegerField(null=True)
    experimentalist = ForeignKeyField(db_column='experimentalist_id', rel_model=Users, to_field='id')
    legacy_date_run = DateField(null=True)
    legacy_incubation_time_minutes = FloatField(null=True)
    legacy_plate_name = CharField(unique=True)
    legacy_treatment_time = TimeField(null=True)
    notes = CharField(null=True)
    plate = ForeignKeyField(db_column='plate_id', rel_model=Plates, to_field='id')
    sauron_configuration = ForeignKeyField(db_column='sauron_configuration_id', rel_model=SauronConfigurations, to_field='id')
    sauronx_commit_sha1 = CharField(null=True)
    suspicious = IntegerField()

    class Meta:
        db_table = 'plate_runs'

class Sensors(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'sensors'

class SensorData(BaseModel):
    floats = TextField()
    floats_sha1 = CharField()
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    sensor = ForeignKeyField(db_column='sensor_id', rel_model=Sensors, to_field='id')

    class Meta:
        db_table = 'sensor_data'

class StimulusSourceSynonyms(BaseModel):
    name = CharField(unique=True)
    stimulus_source = ForeignKeyField(db_column='stimulus_source_id', rel_model=StimulusSources, to_field='id')

    class Meta:
        db_table = 'stimulus_source_synonyms'

class StrainStages(BaseModel):
    generation = IntegerField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'strain_stages'

class Strains(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    date_created = DateField(null=True)
    father_strain = ForeignKeyField(db_column='father_strain_id', null=True, rel_model='self', to_field='id')
    father_strain_name = CharField(null=True)
    injection_hgnc_gene_symbol = CharField(null=True)
    mother_strain = ForeignKeyField(db_column='mother_strain_id', null=True, rel_model='self', related_name='strains_mother_strain_set', to_field='id')
    mother_strain_name = CharField(null=True)
    name = CharField(unique=True)
    notes = CharField(null=True)
    stage = ForeignKeyField(db_column='stage_id', null=True, rel_model=StrainStages, to_field='id')

    class Meta:
        db_table = 'strains'

class StrainSynonyms(BaseModel):
    name = CharField(unique=True)
    strain = ForeignKeyField(db_column='strain_id', rel_model=Strains, to_field='id')

    class Meta:
        db_table = 'strain_synonyms'

class Targets(BaseModel):
    external = CharField(db_column='external_id')
    hgnc_gene_symbol = CharField(index=True, null=True)
    source = ForeignKeyField(db_column='source_id', rel_model=DataSources, to_field='id')

    class Meta:
        db_table = 'targets'
        indexes = (
            (('source', 'external'), True),
        )

class TargetBindingEvents(BaseModel):
    affinity = FloatField(null=True)
    binding_mode = ForeignKeyField(db_column='binding_mode_id', null=True, rel_model=BindingModes, to_field='id')
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    source = ForeignKeyField(db_column='source_id', rel_model=DataSources, to_field='id')
    target = ForeignKeyField(db_column='target_id', rel_model=Targets, to_field='id')

    class Meta:
        db_table = 'target_binding_events'
        indexes = (
            (('compound', 'target'), False),
            (('compound', 'target', 'binding_mode'), False),
            (('compound', 'target', 'source'), False),
            (('compound', 'target', 'source', 'binding_mode'), False),
            (('source', 'compound', 'target', 'binding_mode'), True),
        )

class Treatments(BaseModel):
    micromolar_dose = FloatField(null=True)
    name = CharField(null=True, unique=True)
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', null=True, rel_model=OrderedCompounds, to_field='id')

    class Meta:
        db_table = 'treatments'
        indexes = (
            (('ordered_compound', 'micromolar_dose'), True),
        )

class Wells(BaseModel):
    approx_n_fish = IntegerField(null=True)
    control_status = CharField(null=True)
    created = DateTimeField()
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    strain = ForeignKeyField(db_column='strain_id', null=True, rel_model=Strains, to_field='id')
    well_group = IntegerField(index=True, null=True)
    well_index = IntegerField()

    class Meta:
        db_table = 'wells'
        indexes = (
            (('plate_run', 'control_status'), False),
            (('plate_run', 'well_index'), True),
        )

class WellConditions(BaseModel):
    micromolar_dose = FloatField(null=True)
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', rel_model=OrderedCompounds, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_conditions'
        indexes = (
            (('well', 'ordered_compound'), True),
        )

class WellFeatures(BaseModel):
    external_uri = CharField(null=True)
    floats = TextField(null=True)
    sha1 = CharField()
    type = ForeignKeyField(db_column='type_id', rel_model=FeatureTypes, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_features'
        indexes = (
            (('well', 'type'), True),
        )

class WellFrameImages(BaseModel):
    created = DateTimeField()
    frame = IntegerField()
    png = TextField()
    png_sha1 = CharField()
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_frame_images'
        indexes = (
            (('well', 'frame'), True),
        )

class WellLayouts(BaseModel):
    approx_n_fish = IntegerField(null=True)
    control_status = CharField(null=True)
    plate_layout = IntegerField(db_column='plate_layout_id', index=True)
    strain = ForeignKeyField(db_column='strain_id', null=True, rel_model=Strains, to_field='id')
    well_index = IntegerField()

    class Meta:
        db_table = 'well_layouts'
        indexes = (
            (('plate_layout', 'well_index'), False),
            (('plate_layout', 'well_index'), True),
        )

class WellTreatments(BaseModel):
    treatment = ForeignKeyField(db_column='treatment_id', rel_model=Treatments, to_field='id')
    well_layout = ForeignKeyField(db_column='well_layout_id', rel_model=WellLayouts, to_field='id')

    class Meta:
        db_table = 'well_treatments'
        indexes = (
            (('well_layout', 'treatment'), False),
            (('well_layout', 'treatment'), True),
        )

