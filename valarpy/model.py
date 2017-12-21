from peewee import *
from valarpy.global_connection import db
database = db.peewee_database


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class ApiKeys(BaseModel):
    name = CharField()
    value = CharField()

    class Meta:
        db_table = 'api_keys'

class Users(BaseModel):
    bcrypt_hash = CharField(index=True, null=True)
    created = DateTimeField()
    first_name = CharField(index=True)
    last_name = CharField(index=True)
    username = CharField(unique=True)
    write_access = IntegerField(index=True)

    class Meta:
        db_table = 'users'

class TemplateAssays(BaseModel):
    author = ForeignKeyField(db_column='author_id', null=True, rel_model=Users, to_field='id')
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)
    specializes = ForeignKeyField(db_column='specializes', null=True, rel_model='self', to_field='id')

    class Meta:
        db_table = 'template_assays'

class Assays(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    hidden = IntegerField()
    length = IntegerField()
    name = CharField(unique=True)
    template_assay = ForeignKeyField(db_column='template_assay_id', null=True, rel_model=TemplateAssays, to_field='id')

    class Meta:
        db_table = 'assays'
        indexes = (
            (('name', 'frames_sha1'), True),
        )

class AssayParams(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    name = CharField()
    value = FloatField()

    class Meta:
        db_table = 'assay_params'
        indexes = (
            (('name', 'assay'), True),
        )

class Protocols(BaseModel):
    assays_sha1 = BlobField(unique=True)  # auto-corrected to BlobField
    author = ForeignKeyField(db_column='author_id', null=True, rel_model=Users, to_field='id')
    created = DateTimeField()
    description = CharField(null=True)
    hidden = IntegerField()
    length = IntegerField(index=True)
    name = CharField(unique=True)
    notes = CharField(null=True)
    template = IntegerField(db_column='template_id', index=True, null=True)

    class Meta:
        db_table = 'protocols'

class AssaysInProtocols(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Protocols, to_field='id')
    start = IntegerField(index=True)

    class Meta:
        db_table = 'assays_in_protocols'
        indexes = (
            (('protocol', 'assay', 'start'), True),
        )

class AudioFiles(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    data = BlobField()  # auto-corrected to BlobField
    filename = CharField(unique=True)
    n_seconds = FloatField()
    notes = CharField(null=True)
    sha1 = BlobField(unique=True)  # auto-corrected to BlobField

    class Meta:
        db_table = 'audio_files'

class Cameras(BaseModel):
    connection_type = CharField()
    created = DateTimeField(null=True)
    description = TextField(null=True)
    model = CharField()
    name = CharField(index=True)
    serial_number = IntegerField(index=True, null=True)

    class Meta:
        db_table = 'cameras'

class CameraConfigs(BaseModel):
    brightness = FloatField(null=True)
    camera = ForeignKeyField(db_column='camera_id', rel_model=Cameras, to_field='id')
    clockwise_degrees_to_rotate_image = FloatField(null=True)
    contrast = FloatField(null=True)
    created = DateTimeField()
    exposure = FloatField(null=True)
    fourcc = BlobField(null=True)  # auto-corrected to BlobField
    frame_height = IntegerField(null=True)
    frame_width = IntegerField(null=True)
    frames_per_second = IntegerField(null=True)
    gain = FloatField(null=True)
    gamma = FloatField(null=True)
    hue = FloatField(null=True)
    mode = IntegerField(null=True)
    roi_x0 = FloatField(null=True)
    roi_x1 = FloatField(null=True)
    roi_y1 = FloatField(null=True)
    roi_y2 = FloatField(null=True)
    saturation = FloatField(null=True)
    sharpness = FloatField(null=True)
    startup_wait_seconds = FloatField(null=True)

    class Meta:
        db_table = 'camera_configs'

class PlateTypes(BaseModel):
    height_millimeters = FloatField(null=True)
    manufacturer = CharField(null=True)
    n_columns = IntegerField()
    n_rows = IntegerField()
    opacity = CharField()
    part_number = CharField(null=True)
    well_shape = CharField()
    width_millimeters = FloatField(null=True)

    class Meta:
        db_table = 'plate_types'
        indexes = (
            (('manufacturer', 'part_number'), False),
            (('n_rows', 'n_columns'), False),
        )

class Superprojects(BaseModel):
    active = IntegerField()
    created = DateTimeField()
    description = CharField(null=True)
    methods = TextField(null=True)
    name = CharField(unique=True)
    primary_author = ForeignKeyField(db_column='primary_author_id', null=True, rel_model=Users, to_field='id')
    reason = TextField(null=True)

    class Meta:
        db_table = 'superprojects'

class TemplatePlates(BaseModel):
    author = ForeignKeyField(db_column='author_id', rel_model=Users, to_field='id')
    created = DateTimeField()
    description = CharField(null=True)
    hidden = IntegerField()
    name = CharField(unique=True)
    plate_type = ForeignKeyField(db_column='plate_type_id', rel_model=PlateTypes, to_field='id')
    solvent_dose_type = CharField()
    specializes = ForeignKeyField(db_column='specializes', null=True, rel_model='self', to_field='id')

    class Meta:
        db_table = 'template_plates'

class Projects(BaseModel):
    active = IntegerField(null=True)
    created = DateTimeField()
    default_dark_adaptation_seconds = IntegerField()
    description = CharField(null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Protocols, to_field='id')
    superproject = ForeignKeyField(db_column='superproject_id', null=True, rel_model=Superprojects, to_field='id')
    template_plate = ForeignKeyField(db_column='template_plate_id', null=True, rel_model=TemplatePlates, to_field='id')

    class Meta:
        db_table = 'projects'

class Plates(BaseModel):
    created = DateTimeField()
    datetime_fish_plated = DateTimeField(index=True, null=True)
    person_plated = ForeignKeyField(db_column='person_plated_id', rel_model=Users, to_field='id')
    plate_type = ForeignKeyField(db_column='plate_type_id', null=True, rel_model=PlateTypes, to_field='id')
    project = ForeignKeyField(db_column='project_id', rel_model=Projects, to_field='id')

    class Meta:
        db_table = 'plates'

class Saurons(BaseModel):
    created = DateTimeField()
    current = IntegerField(index=True)
    number = IntegerField(index=True)

    class Meta:
        db_table = 'saurons'

class SauronConfigs(BaseModel):
    camera_config = ForeignKeyField(db_column='camera_config_id', null=True, rel_model=CameraConfigs, to_field='id')
    created = DateTimeField()
    datetime_changed = DateTimeField()
    description = TextField()
    sauron = ForeignKeyField(db_column='sauron_id', rel_model=Saurons, to_field='id')

    class Meta:
        db_table = 'sauron_configs'
        indexes = (
            (('sauron', 'datetime_changed'), True),
        )

class SauronxSubmissions(BaseModel):
    created = DateTimeField()
    dark_adaptation_time_seconds = IntegerField()
    datetime_dosed = DateTimeField(null=True)
    datetime_fish_plated = DateTimeField()
    id_hash_hex = CharField(unique=True)
    notes = TextField(null=True)
    person_plated = ForeignKeyField(db_column='person_plated_id', rel_model=Users, to_field='id')
    project = ForeignKeyField(db_column='project_id', rel_model=Projects, to_field='id')
    same_plate_submission = ForeignKeyField(db_column='same_plate_submission_id', null=True, rel_model='self', to_field='id')
    short_description = CharField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, related_name='users_user_set', to_field='id')

    class Meta:
        db_table = 'sauronx_submissions'

class SauronxTomls(BaseModel):
    created = DateTimeField()
    text_sha1 = BlobField(unique=True)  # auto-corrected to BlobField
    toml_text = TextField()

    class Meta:
        db_table = 'sauronx_tomls'

class PlateRuns(BaseModel):
    calculated_mean_framerate = FloatField()
    concern_level = CharField(index=True, null=True)
    created = DateTimeField()
    dark_adaptation_seconds = IntegerField(index=True, null=True)
    datetime_dosed = DateTimeField(index=True, null=True)
    datetime_run = DateTimeField(index=True)
    experimentalist = ForeignKeyField(db_column='experimentalist_id', rel_model=Users, to_field='id')
    incubation_minutes = IntegerField(index=True, null=True)
    legacy_name = CharField(index=True, null=True)
    notes = TextField(null=True)
    plate = ForeignKeyField(db_column='plate_id', rel_model=Plates, to_field='id')
    project = ForeignKeyField(db_column='project_id', rel_model=Projects, to_field='id')
    sauron_config = ForeignKeyField(db_column='sauron_config_id', rel_model=SauronConfigs, to_field='id')
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission_id', null=True, rel_model=SauronxSubmissions, to_field='id')
    sauronx_toml = ForeignKeyField(db_column='sauronx_toml_id', null=True, rel_model=SauronxTomls, to_field='id')
    short_description = CharField()

    class Meta:
        db_table = 'plate_runs'

class CarpTasks(BaseModel):
    days_to_wait = IntegerField(null=True)
    description = TextField(null=True)
    failure_condition = CharField(null=True)
    failure_target = IntegerField(db_column='failure_target_id', index=True, null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    project_type = IntegerField(index=True)
    success_condition = CharField(null=True)
    success_target = IntegerField(db_column='success_target_id', index=True, null=True)

    class Meta:
        db_table = 'carp_tasks'

class CarpDataTypes(BaseModel):
    description = TextField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'carp_data_types'

class CarpDataTasks(BaseModel):
    data_type_produced = ForeignKeyField(db_column='data_type_produced', rel_model=CarpDataTypes, to_field='id')
    description = TextField(null=True)
    name = CharField()
    task = ForeignKeyField(db_column='task_id', rel_model=CarpTasks, to_field='id')

    class Meta:
        db_table = 'carp_data_tasks'
        indexes = (
            (('name', 'task'), True),
        )

class FishVariants(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    date_created = DateField(null=True)
    father_fish_variant = ForeignKeyField(db_column='father_fish_variant_id', null=True, rel_model='self', to_field='id')
    lineage_type = CharField(index=True, null=True)
    mother_fish_variant = ForeignKeyField(db_column='mother_fish_variant_id', null=True, rel_model='self', related_name='fish_variants_mother_fish_variant_set', to_field='id')
    name = CharField(unique=True)
    notes = CharField(null=True)

    class Meta:
        db_table = 'fish_variants'

class CarpProjectTypes(BaseModel):
    base_type = CharField()
    description = TextField(null=True)
    name = CharField(unique=True)
    primary_user = ForeignKeyField(db_column='primary_user', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'carp_project_types'

class CarpProjects(BaseModel):
    ancestor = ForeignKeyField(db_column='ancestor_id', null=True, rel_model='self', to_field='id')
    created = DateTimeField()
    description = TextField(null=True)
    modified = DateTimeField()
    name = CharField(unique=True)
    owner = ForeignKeyField(db_column='owner_id', null=True, rel_model=Users, to_field='id')
    project_type = ForeignKeyField(db_column='project_type_id', null=True, rel_model=CarpProjectTypes, to_field='id')

    class Meta:
        db_table = 'carp_projects'

class CarpTanks(BaseModel):
    birthdate = DateField()
    created = DateTimeField()
    fish_variant = ForeignKeyField(db_column='fish_variant_id', rel_model=FishVariants, to_field='id')
    internal = CharField(db_column='internal_id', unique=True)
    notes = TextField(null=True)
    project = ForeignKeyField(db_column='project_id', rel_model=CarpProjects, to_field='id')

    class Meta:
        db_table = 'carp_tanks'

class CarpData(BaseModel):
    created = DateTimeField()
    data_task = ForeignKeyField(db_column='data_task_id', rel_model=CarpDataTasks, to_field='id')
    external_uri = TextField(null=True)
    father_tank = ForeignKeyField(db_column='father_tank', rel_model=CarpTanks, to_field='id')
    file_blob = BlobField(null=True)  # auto-corrected to BlobField
    file_blob_sha1 = BlobField(index=True, null=True)  # auto-corrected to BlobField
    mother_tank = ForeignKeyField(db_column='mother_tank', rel_model=CarpTanks, related_name='carp_tanks_mother_tank_set', to_field='id')
    notes = TextField(null=True)
    person_collected = ForeignKeyField(db_column='person_collected', rel_model=Users, to_field='id')
    plate_run = ForeignKeyField(db_column='plate_run_id', null=True, rel_model=PlateRuns, to_field='id')

    class Meta:
        db_table = 'carp_data'

class CarpScans(BaseModel):
    created = DateTimeField()
    datetime_scanned = DateTimeField()
    person_scanned = ForeignKeyField(db_column='person_scanned_id', rel_model=Users, to_field='id')
    scan_type = CharField()
    scan_value = CharField()
    tank = ForeignKeyField(db_column='tank_id', rel_model=CarpTanks, to_field='id')

    class Meta:
        db_table = 'carp_scans'

class CarpSystemData(BaseModel):
    created = DateTimeField()
    datetime_scanned = DateTimeField()
    name = CharField()
    value = CharField()

    class Meta:
        db_table = 'carp_system_data'
        indexes = (
            (('name', 'datetime_scanned'), True),
        )

class CarpTankTasks(BaseModel):
    created = DateTimeField()
    notes = CharField()
    tank = ForeignKeyField(db_column='tank_id', rel_model=CarpTanks, to_field='id')
    task = ForeignKeyField(db_column='task_id', rel_model=CarpTasks, to_field='id')

    class Meta:
        db_table = 'carp_tank_tasks'

class Sensors(BaseModel):
    blob_type = CharField(null=True)
    created = DateTimeField()
    data_type = CharField()
    description = CharField(null=True)
    n_between = IntegerField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'sensors'

class Stimuli(BaseModel):
    analog = IntegerField()
    audio_file = ForeignKeyField(db_column='audio_file_id', null=True, rel_model=AudioFiles, to_field='id', unique=True)
    created = DateTimeField()
    default_color = CharField()
    description = CharField(null=True)
    name = CharField(unique=True)
    rgb = BlobField(null=True)  # auto-corrected to BlobField
    wavelength_nanometers = IntegerField(null=True)

    class Meta:
        db_table = 'stimuli'

class ComponentChecks(BaseModel):
    created = DateTimeField()
    data = BlobField(null=True)  # auto-corrected to BlobField
    datetime_scanned = DateTimeField()
    name = CharField()
    sauron_config = ForeignKeyField(db_column='sauron_config_id', rel_model=SauronConfigs, to_field='id')
    sensor = ForeignKeyField(db_column='sensor_id', rel_model=Sensors, to_field='id')
    stimulus = ForeignKeyField(db_column='stimulus_id', null=True, rel_model=Stimuli, to_field='id')
    value = CharField(null=True)

    class Meta:
        db_table = 'component_checks'
        indexes = (
            (('name', 'datetime_scanned'), True),
        )

class CompoundSources(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'compound_sources'

class DataSources(BaseModel):
    created = DateTimeField()
    date_time_downloaded = DateTimeField(null=True)
    description = CharField(null=True)
    external_version = CharField(null=True)
    name = CharField(index=True)
    url = CharField(index=True, null=True)

    class Meta:
        db_table = 'data_sources'
        indexes = (
            (('name', 'external_version'), True),
        )

class Compounds(BaseModel):
    chembl = CharField(db_column='chembl_id', null=True, unique=True)
    chemspider = IntegerField(db_column='chemspider_id', null=True)
    created = DateTimeField()
    inchi = CharField()
    inchikey = CharField(unique=True)
    inchikey_connectivity = CharField(index=True)
    smiles = CharField(null=True)

    class Meta:
        db_table = 'compounds'

class OrderedCompounds(BaseModel):
    box_number = IntegerField(index=True, null=True)
    compound = ForeignKeyField(db_column='compound_id', null=True, rel_model=Compounds, to_field='id')
    compound_source = ForeignKeyField(db_column='compound_source_id', null=True, rel_model=CompoundSources, to_field='id')
    concentration_millimolar = FloatField(null=True)
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', null=True, rel_model=DataSources, to_field='id')
    date_ordered = DateField(index=True, null=True)
    external = CharField(db_column='external_id', index=True, null=True)
    legacy_internal = CharField(db_column='legacy_internal_id', index=True, null=True)
    location = CharField(null=True)
    molecular_weight = FloatField(null=True)
    notes = TextField(null=True)
    person_ordered = ForeignKeyField(db_column='person_ordered', null=True, rel_model=Users, to_field='id')
    reason_ordered = TextField(null=True)
    solvent = ForeignKeyField(db_column='solvent_id', null=True, rel_model=Compounds, related_name='compounds_solvent_set', to_field='id')
    supplier_catalog_number = CharField(null=True)
    suspicious = IntegerField()
    unique_hash = CharField(unique=True)
    well_number = IntegerField(index=True, null=True)

    class Meta:
        db_table = 'ordered_compounds'
        indexes = (
            (('box_number', 'well_number'), True),
        )

class CompoundIds(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    external = CharField(db_column='external_id', index=True)
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', rel_model=OrderedCompounds, to_field='id')

    class Meta:
        db_table = 'compound_ids'
        indexes = (
            (('ordered_compound', 'data_source'), True),
        )

class CompoundNames(BaseModel):
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    name = CharField()

    class Meta:
        db_table = 'compound_names'

class ControlTypes(BaseModel):
    description = CharField()
    drug_related = IntegerField(index=True)
    genetics_related = IntegerField(index=True)
    name = CharField(unique=True)
    positive = IntegerField(index=True)

    class Meta:
        db_table = 'control_types'

class Wells(BaseModel):
    approx_n_fish = IntegerField(index=True, null=True)
    control_type = ForeignKeyField(db_column='control_type', null=True, rel_model=ControlTypes, to_field='id')
    created = DateTimeField()
    days_post_fertilization = IntegerField()
    fish_variant = ForeignKeyField(db_column='fish_variant_id', null=True, rel_model=FishVariants, to_field='id')
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    well_group = IntegerField(index=True, null=True)
    well_index = IntegerField(index=True)

    class Meta:
        db_table = 'wells'
        indexes = (
            (('plate_run', 'well_index'), True),
        )

class Concerns(BaseModel):
    annotator = ForeignKeyField(db_column='annotator_id', rel_model=Users, to_field='id')
    assay = ForeignKeyField(db_column='assay_id', null=True, rel_model=Assays, to_field='id')
    created = DateTimeField()
    explanation = TextField(null=True)
    level = CharField(index=True)
    name = CharField(index=True, null=True)
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    submission = ForeignKeyField(db_column='submission_id', null=True, rel_model=SauronxSubmissions, to_field='id')
    well = ForeignKeyField(db_column='well_id', null=True, rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'concerns'

class ConditionTypes(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator', rel_model=Users, to_field='id')
    description = CharField()
    kind = CharField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'condition_types'

class Features(BaseModel):
    created = DateTimeField()
    data_type = CharField()
    description = CharField()
    dimensions = CharField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'features'

class Genes(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    uniprot = CharField(db_column='uniprot_id', null=True, unique=True)
    zfin = CharField(db_column='zfin_id', null=True, unique=True)

    class Meta:
        db_table = 'genes'

class Locations(BaseModel):
    active = IntegerField()
    created = DateTimeField()
    description = CharField()
    name = CharField(unique=True)
    part_of = ForeignKeyField(db_column='part_of', null=True, rel_model='self', to_field='id')
    purpose = CharField()
    temporary = IntegerField()

    class Meta:
        db_table = 'locations'

class LorienConfigs(BaseModel):
    created = DateTimeField()
    notes = CharField(null=True)

    class Meta:
        db_table = 'lorien_configs'

class MandosKeys(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    external = CharField(db_column='external_id', index=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'mandos_keys'
        indexes = (
            (('data_source', 'external'), True),
        )

class MandosModes(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    external = CharField(db_column='external_id', null=True)
    kind = CharField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'mandos_modes'

class MandosAssociations(BaseModel):
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    external = CharField(db_column='external_id', index=True, null=True)
    key = ForeignKeyField(db_column='key_id', rel_model=MandosKeys, to_field='id')
    mode = ForeignKeyField(db_column='mode_id', null=True, rel_model=MandosModes, to_field='id')
    value = CharField(null=True)

    class Meta:
        db_table = 'mandos_associations'
        indexes = (
            (('data_source', 'compound', 'key', 'mode'), True),
        )

class MandosChemInfo(BaseModel):
    compound = IntegerField(db_column='compound_id')
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=DataSources, to_field='id')
    name = CharField(index=True)
    value = CharField(index=True)

    class Meta:
        db_table = 'mandos_chem_info'
        indexes = (
            (('name', 'data_source'), True),
        )

class Plasmids(BaseModel):
    ape_file = BlobField()  # auto-corrected to BlobField
    ape_file_sha1 = BlobField(unique=True)  # auto-corrected to BlobField
    box_number = IntegerField()
    created = DateTimeField()
    gene = ForeignKeyField(db_column='gene_id', null=True, rel_model=Genes, to_field='id')
    tube_number = IntegerField()
    use_case = CharField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'plasmids'
        indexes = (
            (('box_number', 'tube_number'), True),
        )

class Mutations(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    endogenous_gene = ForeignKeyField(db_column='endogenous_gene_id', null=True, rel_model=Genes, to_field='id')
    fish_variant = ForeignKeyField(db_column='fish_variant_id', null=True, rel_model=FishVariants, to_field='id')
    plasmid = ForeignKeyField(db_column='plasmid_id', null=True, rel_model=Plasmids, to_field='id')
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'mutations'

class Oligos(BaseModel):
    created = DateTimeField()
    mutation = ForeignKeyField(db_column='mutation_id', null=True, rel_model=Mutations, to_field='id')
    plasmid = ForeignKeyField(db_column='plasmid_id', null=True, rel_model=Plasmids, to_field='id')
    sequence = TextField()
    used_for = TextField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'oligos'

class PlateRunInfo(BaseModel):
    name = CharField()
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    value = CharField()

    class Meta:
        db_table = 'plate_run_info'
        indexes = (
            (('plate_run', 'name'), True),
        )

class Rois(BaseModel):
    lorien_commit_sha1 = BlobField(index=True, null=True)  # auto-corrected to BlobField
    lorien_config = IntegerField(index=True, null=True)
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')
    x0 = IntegerField()
    x1 = IntegerField()
    y0 = IntegerField()
    y1 = IntegerField()

    class Meta:
        db_table = 'rois'

class SauronxSubmissionHistory(BaseModel):
    created = DateTimeField()
    datetime_modified = DateTimeField()
    sauron = ForeignKeyField(db_column='sauron_id', rel_model=Saurons, to_field='id')
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission_id', rel_model=SauronxSubmissions, to_field='id')
    status = CharField(null=True)

    class Meta:
        db_table = 'sauronx_submission_history'
        indexes = (
            (('sauronx_submission', 'status', 'datetime_modified'), True),
        )

class SauronxSubmissionParams(BaseModel):
    name = CharField()
    param_type = CharField()
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission_id', rel_model=SauronxSubmissions, to_field='id')
    value = CharField()

    class Meta:
        db_table = 'sauronx_submission_params'
        indexes = (
            (('sauronx_submission', 'name'), True),
        )

class SensorData(BaseModel):
    floats = BlobField()  # auto-corrected to BlobField
    floats_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    plate_run = ForeignKeyField(db_column='plate_run_id', rel_model=PlateRuns, to_field='id')
    sensor = ForeignKeyField(db_column='sensor_id', rel_model=Sensors, to_field='id')

    class Meta:
        db_table = 'sensor_data'

class StimulusFrames(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    frames = BlobField()  # auto-corrected to BlobField
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    stimulus = ForeignKeyField(db_column='stimulus_id', rel_model=Stimuli, to_field='id')

    class Meta:
        db_table = 'stimulus_frames'
        indexes = (
            (('assay', 'stimulus'), True),
        )

class TemplateStimulusFrames(BaseModel):
    range_expression = CharField()
    stimulus = ForeignKeyField(db_column='stimulus_id', rel_model=Stimuli, to_field='id')
    template_assay = ForeignKeyField(db_column='template_assay_id', rel_model=TemplateAssays, to_field='id')
    value_expression = CharField()

    class Meta:
        db_table = 'template_stimulus_frames'

class TemplateTreatments(BaseModel):
    dose_expression = CharField()
    ordered_compound_expression = CharField()
    template_plate = ForeignKeyField(db_column='template_plate_id', rel_model=TemplatePlates, to_field='id')
    well_range_expression = CharField()

    class Meta:
        db_table = 'template_treatments'

class TemplateWells(BaseModel):
    age_dpf_expression = CharField()
    control_type = ForeignKeyField(db_column='control_type', null=True, rel_model=ControlTypes, to_field='id')
    fish_variant_expression = CharField()
    n_fish_expression = CharField()
    template_plate = ForeignKeyField(db_column='template_plate_id', rel_model=TemplatePlates, to_field='id')
    well_range_expression = CharField()

    class Meta:
        db_table = 'template_wells'

class WellFeatures(BaseModel):
    floats = BlobField()  # auto-corrected to BlobField
    lorien_commit_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    lorien_config = ForeignKeyField(db_column='lorien_config_id', rel_model=LorienConfigs, to_field='id')
    sha1 = BlobField(index=True)  # auto-corrected to BlobField
    type = ForeignKeyField(db_column='type_id', rel_model=Features, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_features'
        indexes = (
            (('well', 'type', 'lorien_config'), True),
        )

class WellTreatments(BaseModel):
    micromolar_dose = FloatField(null=True)
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', rel_model=OrderedCompounds, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_treatments'
        indexes = (
            (('well', 'ordered_compound'), True),
        )

