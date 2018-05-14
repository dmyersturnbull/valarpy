from peewee import *
from valarpy.global_connection import db
database = db.peewee_database


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Suppliers(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'suppliers'

class Users(BaseModel):
    bcrypt_hash = CharField(index=True, null=True)
    created = DateTimeField()
    first_name = CharField(index=True)
    last_name = CharField(index=True)
    username = CharField(unique=True)
    write_access = IntegerField(index=True)

    class Meta:
        db_table = 'users'

class PlateTypes(BaseModel):
    datetime_prepared = DateTimeField(null=True)
    n_columns = IntegerField()
    n_rows = IntegerField()
    opacity = CharField()
    part_number = CharField(index=True, null=True)
    set_up_by = ForeignKeyField(db_column='set_up_by', null=True, rel_model=Users, to_field='id')
    supplier = ForeignKeyField(db_column='supplier_id', null=True, rel_model=Suppliers, to_field='id')
    well_shape = CharField()

    class Meta:
        db_table = 'plate_types'
        indexes = (
            (('n_rows', 'n_columns'), False),
        )

class Batteries(BaseModel):
    assays_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    author = ForeignKeyField(db_column='author_id', null=True, rel_model=Users, to_field='id')
    created = DateTimeField()
    description = CharField(null=True)
    hidden = IntegerField()
    length = IntegerField(index=True)
    name = CharField(unique=True)
    notes = CharField(null=True)
    template = IntegerField(db_column='template_id', index=True, null=True)

    class Meta:
        db_table = 'batteries'

class ProjectTypes(BaseModel):
    description = TextField()
    name = CharField(unique=True)

    class Meta:
        db_table = 'project_types'

class Superprojects(BaseModel):
    active = IntegerField()
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', rel_model=Users, to_field='id')
    description = CharField(null=True)
    methods = TextField(null=True)
    name = CharField(unique=True)
    reason = TextField(null=True)
    type = ForeignKeyField(db_column='type_id', null=True, rel_model=ProjectTypes, to_field='id')

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

class Experiments(BaseModel):
    active = IntegerField(null=True)
    created = DateTimeField()
    creator = IntegerField(db_column='creator_id')
    default_acclimation_sec = IntegerField()
    description = CharField(null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    project = ForeignKeyField(db_column='project_id', rel_model=Superprojects, to_field='id')
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Batteries, to_field='id')
    template_plate = ForeignKeyField(db_column='template_plate_id', null=True, rel_model=TemplatePlates, to_field='id')

    class Meta:
        db_table = 'experiments'

class Plates(BaseModel):
    created = DateTimeField()
    datetime_fish_plated = DateTimeField(index=True, null=True)
    person_plated = ForeignKeyField(db_column='person_plated_id', rel_model=Users, to_field='id')
    plate_type = ForeignKeyField(db_column='plate_type_id', null=True, rel_model=PlateTypes, to_field='id')
    project = ForeignKeyField(db_column='project_id', rel_model=Experiments, to_field='id')

    class Meta:
        db_table = 'plates'

class Saurons(BaseModel):
    active = IntegerField(index=True)
    created = DateTimeField()
    number = IntegerField(index=True)

    class Meta:
        db_table = 'saurons'

class SauronConfigs(BaseModel):
    created = DateTimeField()
    datetime_changed = DateTimeField()
    description = TextField()
    sauron = ForeignKeyField(db_column='sauron_id', rel_model=Saurons, to_field='id')

    class Meta:
        db_table = 'sauron_configs'
        indexes = (
            (('sauron', 'datetime_changed'), True),
        )

class Submissions(BaseModel):
    acclimation_seconds = IntegerField(null=True)
    created = DateTimeField()
    datetime_dosed = DateTimeField(null=True)
    datetime_fish_plated = DateTimeField()
    id_hash_hex = CharField(unique=True)
    notes = TextField(null=True)
    person_plated = ForeignKeyField(db_column='person_plated_id', rel_model=Users, to_field='id')
    project = ForeignKeyField(db_column='project_id', rel_model=Experiments, to_field='id')
    same_plate_submission = ForeignKeyField(db_column='same_plate_submission_id', null=True, rel_model='self', to_field='id')
    short_description = CharField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, related_name='users_user_set', to_field='id')

    class Meta:
        db_table = 'submissions'

class ConfigFiles(BaseModel):
    created = DateTimeField()
    text_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    toml_text = TextField()

    class Meta:
        db_table = 'config_files'

class Runs(BaseModel):
    acclimation_seconds = IntegerField(index=True, null=True)
    created = DateTimeField()
    datetime_dosed = DateTimeField(index=True, null=True)
    datetime_run = DateTimeField(index=True)
    description = CharField()
    experiment = ForeignKeyField(db_column='experiment_id', rel_model=Experiments, to_field='id')
    experimentalist = ForeignKeyField(db_column='experimentalist_id', rel_model=Users, to_field='id')
    incubation_minutes = IntegerField(index=True, null=True)
    name = CharField(index=True)
    notes = TextField(null=True)
    plate = ForeignKeyField(db_column='plate_id', rel_model=Plates, to_field='id')
    sauron_config = ForeignKeyField(db_column='sauron_config_id', rel_model=SauronConfigs, to_field='id')
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission', null=True, rel_model=Submissions, to_field='id')
    sauronx_toml = ForeignKeyField(db_column='sauronx_toml_id', null=True, rel_model=ConfigFiles, to_field='id')
    tag = CharField()

    class Meta:
        db_table = 'runs'

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
    name = CharField(index=True)
    template_assay = ForeignKeyField(db_column='template_assay_id', null=True, rel_model=TemplateAssays, to_field='id')

    class Meta:
        db_table = 'assays'
        indexes = (
            (('name', 'frames_sha1'), True),
        )

class ControlTypes(BaseModel):
    description = CharField()
    drug_related = IntegerField(index=True)
    genetics_related = IntegerField(index=True)
    name = CharField(index=True)
    positive = IntegerField(index=True)

    class Meta:
        db_table = 'control_types'

class GeneticVariants(BaseModel):
    created = DateTimeField()
    creator = ForeignKeyField(db_column='creator_id', null=True, rel_model=Users, to_field='id')
    date_created = DateField(null=True)
    father_fish_variant = ForeignKeyField(db_column='father_fish_variant_id', null=True, rel_model='self', to_field='id')
    lineage_type = CharField(index=True, null=True)
    mother_fish_variant = ForeignKeyField(db_column='mother_fish_variant_id', null=True, rel_model='self', related_name='genetic_variants_mother_fish_variant_set', to_field='id')
    name = CharField(unique=True)
    notes = TextField(null=True)

    class Meta:
        db_table = 'genetic_variants'

class Wells(BaseModel):
    age = IntegerField(null=True)
    control_type = ForeignKeyField(db_column='control_type', null=True, rel_model=ControlTypes, to_field='id')
    created = DateTimeField()
    n = IntegerField(index=True)
    plate_run = IntegerField(db_column='plate_run_id', index=True)
    variant = ForeignKeyField(db_column='variant_id', null=True, rel_model=GeneticVariants, to_field='id')
    well_group = CharField(index=True, null=True)
    well_index = IntegerField(index=True)

    class Meta:
        db_table = 'wells'
        indexes = (
            (('plate_run', 'well_index'), True),
        )

class Annotations(BaseModel):
    annotator = ForeignKeyField(db_column='annotator_id', rel_model=Users, to_field='id')
    assay = ForeignKeyField(db_column='assay_id', null=True, rel_model=Assays, to_field='id')
    created = DateTimeField()
    explanation = TextField(null=True)
    level = CharField(index=True)
    name = CharField(index=True, null=True)
    run = ForeignKeyField(db_column='run_id', null=True, rel_model=Runs, to_field='id')
    submission = ForeignKeyField(db_column='submission_id', null=True, rel_model=Submissions, to_field='id')
    value = CharField(null=True)
    well = ForeignKeyField(db_column='well_id', null=True, rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'annotations'

class ApiKeys(BaseModel):
    name = CharField()
    value = CharField()

    class Meta:
        db_table = 'api_keys'

class AssayParams(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    name = CharField()
    value = FloatField()

    class Meta:
        db_table = 'assay_params'
        indexes = (
            (('name', 'assay'), True),
        )

class AssayPositions(BaseModel):
    assay = ForeignKeyField(db_column='assay_id', rel_model=Assays, to_field='id')
    protocol = ForeignKeyField(db_column='protocol_id', rel_model=Batteries, to_field='id')
    start = IntegerField(index=True)

    class Meta:
        db_table = 'assay_positions'
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

class Refs(BaseModel):
    created = DateTimeField()
    date_time_downloaded = DateTimeField(null=True)
    description = CharField(null=True)
    external_version = CharField(null=True)
    name = CharField(index=True)
    url = CharField(index=True, null=True)

    class Meta:
        db_table = 'refs'
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

class Batches(BaseModel):
    box_number = IntegerField(index=True, null=True)
    compound = ForeignKeyField(db_column='compound_id', null=True, rel_model=Compounds, to_field='id')
    concentration_millimolar = FloatField(null=True)
    created = DateTimeField()
    date_ordered = DateField(index=True, null=True)
    kind = CharField()
    legacy_internal = CharField(db_column='legacy_internal_id', index=True, null=True)
    location = CharField(null=True)
    lookup_hash = CharField(unique=True)
    molecular_weight = FloatField(null=True)
    notes = TextField(null=True)
    person_ordered = ForeignKeyField(db_column='person_ordered', null=True, rel_model=Users, to_field='id')
    reason_ordered = TextField(null=True)
    ref = ForeignKeyField(db_column='ref_id', null=True, rel_model=Refs, to_field='id')
    solvent = ForeignKeyField(db_column='solvent_id', null=True, rel_model=Compounds, related_name='compounds_solvent_set', to_field='id')
    supplier_catalog_number = CharField(null=True)
    supplier = IntegerField(db_column='supplier_id', index=True, null=True)
    suspicious = IntegerField()
    tag = CharField(null=True)
    well_number = IntegerField(index=True, null=True)

    class Meta:
        db_table = 'batches'
        indexes = (
            (('box_number', 'well_number'), True),
        )

class BatchLabels(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    external = CharField(db_column='external_id', index=True)
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', rel_model=Batches, to_field='id')

    class Meta:
        db_table = 'batch_labels'

class CarpProjectTypes(BaseModel):
    base_type = CharField()
    description = TextField(null=True)
    name = CharField(unique=True)
    primary_user = ForeignKeyField(db_column='primary_user', null=True, rel_model=Users, to_field='id')

    class Meta:
        db_table = 'carp_project_types'

class CarpTasks(BaseModel):
    days_to_wait = IntegerField(null=True)
    description = TextField(null=True)
    failure_condition = CharField(null=True)
    failure_target = IntegerField(db_column='failure_target_id', index=True, null=True)
    name = CharField(index=True)
    notes = TextField(null=True)
    project_type = ForeignKeyField(db_column='project_type', rel_model=CarpProjectTypes, to_field='id')
    success_condition = CharField(null=True)
    success_target = IntegerField(db_column='success_target_id', index=True, null=True)

    class Meta:
        db_table = 'carp_tasks'
        indexes = (
            (('name', 'project_type'), True),
        )

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
    alive = IntegerField()
    birthdate = DateField(index=True)
    created = DateTimeField()
    fish_variant = ForeignKeyField(db_column='fish_variant_id', rel_model=GeneticVariants, to_field='id')
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
    plate_run = IntegerField(db_column='plate_run_id', index=True, null=True)

    class Meta:
        db_table = 'carp_data'

class CarpScans(BaseModel):
    created = DateTimeField()
    datetime_scanned = DateTimeField(index=True)
    person_scanned = ForeignKeyField(db_column='person_scanned_id', rel_model=Users, to_field='id')
    scan_type = CharField(index=True)
    scan_value = CharField(index=True)
    tank = ForeignKeyField(db_column='tank_id', rel_model=CarpTanks, to_field='id')

    class Meta:
        db_table = 'carp_scans'
        indexes = (
            (('tank', 'scan_type', 'datetime_scanned'), True),
        )

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
    wavelength_nm = IntegerField(null=True)

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

class CompoundLabels(BaseModel):
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    name = CharField()

    class Meta:
        db_table = 'compound_labels'

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
    name = CharField(index=True, null=True)
    pub_link = CharField(index=True, null=True)
    sequence = TextField(null=True)

    class Meta:
        db_table = 'genes'

class GeneLabels(BaseModel):
    created = DateTimeField()
    gene = ForeignKeyField(db_column='gene', rel_model=Genes, to_field='id')
    name = CharField(index=True)
    ref = ForeignKeyField(db_column='ref', rel_model=Refs, to_field='id')

    class Meta:
        db_table = 'gene_labels'
        indexes = (
            (('gene', 'name', 'ref'), True),
        )

class GeneticConstructs(BaseModel):
    ape_file = BlobField()  # auto-corrected to BlobField
    ape_file_sha1 = BlobField(unique=True)  # auto-corrected to BlobField
    box_number = IntegerField()
    created = DateTimeField()
    injection_mix = CharField(null=True)
    kind = CharField()
    tube_number = IntegerField()
    use_case = CharField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'genetic_constructs'
        indexes = (
            (('box_number', 'tube_number'), True),
        )

class GeneticEvents(BaseModel):
    created = DateTimeField()
    description = CharField(null=True)
    endogenous_gene = ForeignKeyField(db_column='endogenous_gene_id', null=True, rel_model=Genes, to_field='id')
    fish_variant = ForeignKeyField(db_column='fish_variant_id', null=True, rel_model=GeneticVariants, to_field='id')
    plasmid = ForeignKeyField(db_column='plasmid_id', null=True, rel_model=GeneticConstructs, to_field='id')
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'genetic_events'

class GenesInMutations(BaseModel):
    gene = ForeignKeyField(db_column='gene_id', rel_model=Genes, to_field='id')
    mutation = ForeignKeyField(db_column='mutation_id', rel_model=GeneticEvents, to_field='id')

    class Meta:
        db_table = 'genes_in_mutations'
        indexes = (
            (('gene', 'mutation'), True),
        )

class GeneticConstructFeatures(BaseModel):
    construct = ForeignKeyField(db_column='construct_id', rel_model=GeneticConstructs, to_field='id')
    gene = ForeignKeyField(db_column='gene_id', rel_model=Genes, to_field='id')

    class Meta:
        db_table = 'genetic_construct_features'
        indexes = (
            (('gene', 'construct'), True),
        )

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

class LogFiles(BaseModel):
    created = DateTimeField()
    text = TextField()
    text_sha1 = BlobField(index=True)  # auto-corrected to BlobField

    class Meta:
        db_table = 'log_files'

class LorienConfigs(BaseModel):
    created = DateTimeField()
    notes = CharField(null=True)

    class Meta:
        db_table = 'lorien_configs'

class MandosInfo(BaseModel):
    compound = IntegerField(db_column='compound_id')
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    name = CharField(index=True)
    value = CharField(index=True)

    class Meta:
        db_table = 'mandos_info'
        indexes = (
            (('name', 'data_source', 'compound'), True),
        )

class MandosObjects(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    external = CharField(db_column='external_id', index=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'mandos_objects'
        indexes = (
            (('data_source', 'external'), True),
        )

class MandosObjectTags(BaseModel):
    created = DateTimeField()
    name = CharField()
    object = ForeignKeyField(db_column='object', rel_model=MandosObjects, to_field='id')
    ref = ForeignKeyField(db_column='ref', rel_model=Refs, to_field='id')
    value = CharField(index=True)

    class Meta:
        db_table = 'mandos_object_tags'
        indexes = (
            (('object', 'ref', 'name', 'value'), True),
        )

class MandosPredicates(BaseModel):
    created = DateTimeField()
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    external = CharField(db_column='external_id', index=True, null=True)
    kind = CharField()
    name = CharField(index=True)

    class Meta:
        db_table = 'mandos_predicates'
        indexes = (
            (('external', 'data_source'), True),
            (('name', 'data_source'), True),
        )

class MandosRules(BaseModel):
    compound = ForeignKeyField(db_column='compound_id', rel_model=Compounds, to_field='id')
    data_source = ForeignKeyField(db_column='data_source_id', rel_model=Refs, to_field='id')
    external = CharField(db_column='external_id', index=True, null=True)
    object = ForeignKeyField(db_column='object_id', rel_model=MandosObjects, to_field='id')
    predicate = ForeignKeyField(db_column='predicate_id', rel_model=MandosPredicates, to_field='id')

    class Meta:
        db_table = 'mandos_rules'
        indexes = (
            (('data_source', 'compound', 'object', 'predicate'), True),
        )

class MandosRuleTags(BaseModel):
    created = DateTimeField()
    name = CharField()
    ref = ForeignKeyField(db_column='ref', rel_model=Refs, to_field='id')
    rule = ForeignKeyField(db_column='rule', rel_model=MandosRules, to_field='id')
    value = CharField(index=True)

    class Meta:
        db_table = 'mandos_rule_tags'
        indexes = (
            (('rule', 'ref', 'name', 'value'), True),
        )

class Rois(BaseModel):
    lorien_commit_sha1 = BlobField(index=True, null=True)  # auto-corrected to BlobField
    lorien_config = ForeignKeyField(db_column='lorien_config', null=True, rel_model=LorienConfigs, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')
    x0 = IntegerField()
    x1 = IntegerField()
    y0 = IntegerField()
    y1 = IntegerField()

    class Meta:
        db_table = 'rois'

class RunTags(BaseModel):
    name = CharField()
    run = ForeignKeyField(db_column='run_id', rel_model=Runs, to_field='id')
    value = CharField()

    class Meta:
        db_table = 'run_tags'
        indexes = (
            (('run', 'name'), True),
        )

class SauronSettings(BaseModel):
    created = DateTimeField()
    name = CharField(index=True)
    sauron = ForeignKeyField(db_column='sauron', rel_model=Saurons, to_field='id')
    value = CharField()

    class Meta:
        db_table = 'sauron_settings'
        indexes = (
            (('sauron', 'name'), True),
        )

class SensorData(BaseModel):
    floats = BlobField()  # auto-corrected to BlobField
    floats_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    run = ForeignKeyField(db_column='run_id', rel_model=Runs, to_field='id')
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

class SubmissionParams(BaseModel):
    name = CharField()
    param_type = CharField(null=True)
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission_id', rel_model=Submissions, to_field='id')
    value = CharField()

    class Meta:
        db_table = 'submission_params'
        indexes = (
            (('sauronx_submission', 'name'), True),
        )

class SubmissionRecords(BaseModel):
    created = DateTimeField()
    datetime_modified = DateTimeField()
    sauron = ForeignKeyField(db_column='sauron_id', rel_model=Saurons, to_field='id')
    sauronx_submission = ForeignKeyField(db_column='sauronx_submission_id', rel_model=Submissions, to_field='id')
    status = CharField(null=True)

    class Meta:
        db_table = 'submission_records'
        indexes = (
            (('sauronx_submission', 'status', 'datetime_modified'), True),
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
    age_expression = CharField()
    control_type = ForeignKeyField(db_column='control_type', null=True, rel_model=ControlTypes, to_field='id')
    fish_variant_expression = CharField()
    group_expression = CharField()
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
    ordered_compound = ForeignKeyField(db_column='ordered_compound_id', rel_model=Batches, to_field='id')
    well = ForeignKeyField(db_column='well_id', rel_model=Wells, to_field='id')

    class Meta:
        db_table = 'well_treatments'
        indexes = (
            (('well', 'ordered_compound'), True),
        )

