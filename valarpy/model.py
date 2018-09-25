from peewee import *
from valarpy.global_connection import db
database = db.peewee_database


class UnknownField(object):
	def __init__(self, *_, **__): pass

class BaseModel(Model):
	class Meta:
		database = database

class Suppliers(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	name = CharField(unique=True)

	class Meta:
		table_name = 'suppliers'

class PlateTypes(BaseModel):
	n_columns = IntegerField()
	n_rows = IntegerField()
	name = CharField(null=True)
	opacity = CharField()
	part_number = CharField(index=True, null=True)
	supplier = ForeignKeyField(column_name='supplier_id', field='id', model=Suppliers, null=True)
	well_shape = CharField()

	class Meta:
		table_name = 'plate_types'
		indexes = (
			(('n_rows', 'n_columns'), False),
		)

class Users(BaseModel):
	bcrypt_hash = CharField(index=True, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	first_name = CharField(index=True)
	last_name = CharField(index=True)
	username = CharField(unique=True)
	write_access = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)

	class Meta:
		table_name = 'users'

class Plates(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_plated = DateTimeField(index=True, null=True)
	person_plated = ForeignKeyField(column_name='person_plated_id', field='id', model=Users)
	plate_type = ForeignKeyField(column_name='plate_type_id', field='id', model=PlateTypes, null=True)

	class Meta:
		table_name = 'plates'

class TransferPlates(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users)
	datetime_created = DateTimeField()
	description = CharField(null=True)
	dilution_factor_from_parent = FloatField(null=True)
	initial_ul_per_well = FloatField()
	name = CharField(unique=True)
	parent = ForeignKeyField(column_name='parent_id', field='id', model='self', null=True)
	plate_type = ForeignKeyField(column_name='plate_type_id', field='id', model=PlateTypes)
	supplier = ForeignKeyField(column_name='supplier_id', field='id', model=Suppliers, null=True)

	class Meta:
		table_name = 'transfer_plates'

class Batteries(BaseModel):
	assays_sha1 = BlobField(index=True)  # auto-corrected to BlobField
	author = ForeignKeyField(column_name='author_id', field='id', model=Users, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
	length = IntegerField(index=True)
	name = CharField(unique=True)
	notes = CharField(null=True)
	template = IntegerField(column_name='template_id', index=True, null=True)

	class Meta:
		table_name = 'batteries'

class ProjectTypes(BaseModel):
	description = TextField()
	name = CharField(unique=True)

	class Meta:
		table_name = 'project_types'

class Superprojects(BaseModel):
	active = IntegerField(constraints=[SQL("DEFAULT 1")])
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users)
	description = CharField(null=True)
	methods = TextField(null=True)
	name = CharField(unique=True)
	reason = TextField(null=True)
	type = ForeignKeyField(column_name='type_id', field='id', model=ProjectTypes, null=True)

	class Meta:
		table_name = 'superprojects'

class TemplatePlates(BaseModel):
	author = ForeignKeyField(column_name='author_id', field='id', model=Users)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
	name = CharField(unique=True)
	plate_type = ForeignKeyField(column_name='plate_type_id', field='id', model=PlateTypes)
	specializes = ForeignKeyField(column_name='specializes', field='id', model='self', null=True)

	class Meta:
		table_name = 'template_plates'

class Experiments(BaseModel):
	active = IntegerField(constraints=[SQL("DEFAULT 1")])
	battery = ForeignKeyField(column_name='battery_id', field='id', model=Batteries)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users)
	default_acclimation_sec = IntegerField()
	description = CharField(null=True)
	name = CharField(unique=True)
	notes = TextField(null=True)
	project = ForeignKeyField(column_name='project_id', field='id', model=Superprojects)
	template_plate = ForeignKeyField(column_name='template_plate_id', field='id', model=TemplatePlates, null=True)
	transfer_plate = ForeignKeyField(column_name='transfer_plate_id', field='id', model=TransferPlates, null=True)

	class Meta:
		table_name = 'experiments'

class Saurons(BaseModel):
	active = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField(index=True)

	class Meta:
		table_name = 'saurons'

class SauronConfigs(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_changed = DateTimeField()
	description = TextField()
	sauron = ForeignKeyField(column_name='sauron_id', field='id', model=Saurons)

	class Meta:
		table_name = 'sauron_configs'
		indexes = (
			(('sauron', 'datetime_changed'), True),
		)

class Submissions(BaseModel):
	acclimation_sec = IntegerField(null=True)
	continuing = ForeignKeyField(column_name='continuing_id', field='id', model='self', null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_dosed = DateTimeField(null=True)
	datetime_plated = DateTimeField()
	description = CharField()
	experiment = ForeignKeyField(column_name='experiment_id', field='id', model=Experiments)
	lookup_hash = CharField(unique=True)
	notes = TextField(null=True)
	person_plated = ForeignKeyField(column_name='person_plated_id', field='id', model=Users)
	user = ForeignKeyField(backref='users_user_set', column_name='user_id', field='id', model=Users)

	class Meta:
		table_name = 'submissions'

class ConfigFiles(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	text_sha1 = BlobField(index=True)  # auto-corrected to BlobField
	toml_text = TextField()

	class Meta:
		table_name = 'config_files'

class Runs(BaseModel):
	acclimation_sec = IntegerField(index=True, null=True)
	config_file = ForeignKeyField(column_name='config_file_id', field='id', model=ConfigFiles, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_dosed = DateTimeField(index=True, null=True)
	datetime_run = DateTimeField(index=True)
	description = CharField()
	experiment = ForeignKeyField(column_name='experiment_id', field='id', model=Experiments)
	experimentalist = ForeignKeyField(column_name='experimentalist_id', field='id', model=Users)
	incubation_min = IntegerField(index=True, null=True)
	name = CharField(index=True, null=True)
	notes = TextField(null=True)
	plate = ForeignKeyField(column_name='plate_id', field='id', model=Plates)
	sauron_config = ForeignKeyField(column_name='sauron_config_id', field='id', model=SauronConfigs)
	submission = ForeignKeyField(column_name='submission_id', field='id', model=Submissions, null=True)
	tag = CharField(constraints=[SQL("DEFAULT ''")])

	class Meta:
		table_name = 'runs'

class TemplateAssays(BaseModel):
	author = ForeignKeyField(column_name='author_id', field='id', model=Users, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	name = CharField(unique=True)
	specializes = ForeignKeyField(column_name='specializes', field='id', model='self', null=True)

	class Meta:
		table_name = 'template_assays'

class Assays(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
	hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
	length = IntegerField()
	name = CharField(unique=True)
	template_assay = ForeignKeyField(column_name='template_assay_id', field='id', model=TemplateAssays, null=True)

	class Meta:
		table_name = 'assays'
		indexes = (
			(('name', 'frames_sha1'), True),
		)

class ControlTypes(BaseModel):
	description = CharField()
	drug_related = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)
	genetics_related = IntegerField(index=True)
	name = CharField(unique=True)
	positive = IntegerField(index=True)

	class Meta:
		table_name = 'control_types'

class GeneticVariants(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users)
	date_created = DateField(null=True)
	father = ForeignKeyField(column_name='father_id', field='id', model='self', null=True)
	fully_annotated = IntegerField(constraints=[SQL("DEFAULT 0")])
	lineage_type = CharField(index=True, null=True)
	mother = ForeignKeyField(backref='genetic_variants_mother_set', column_name='mother_id', field='id', model='self', null=True)
	name = CharField(unique=True)
	notes = TextField(null=True)

	class Meta:
		table_name = 'genetic_variants'

class Wells(BaseModel):
	age = IntegerField(null=True)
	control_type = ForeignKeyField(column_name='control_type_id', field='id', model=ControlTypes, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	n = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
	run = ForeignKeyField(column_name='run_id', field='id', model=Runs)
	variant = ForeignKeyField(column_name='variant_id', field='id', model=GeneticVariants, null=True)
	well_group = CharField(index=True, null=True)
	well_index = IntegerField(index=True)

	class Meta:
		table_name = 'wells'
		indexes = (
			(('run', 'well_index'), True),
		)

class Annotations(BaseModel):
	annotator = ForeignKeyField(column_name='annotator_id', field='id', model=Users)
	assay = ForeignKeyField(column_name='assay_id', field='id', model=Assays, null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = TextField(null=True)
	level = CharField(constraints=[SQL("DEFAULT '1:note'")], index=True)
	name = CharField(index=True, null=True)
	run = ForeignKeyField(column_name='run_id', field='id', model=Runs, null=True)
	submission = ForeignKeyField(column_name='submission_id', field='id', model=Submissions, null=True)
	value = CharField(null=True)
	well = ForeignKeyField(column_name='well_id', field='id', model=Wells, null=True)

	class Meta:
		table_name = 'annotations'

class ApiKeys(BaseModel):
	name = CharField()
	value = CharField()

	class Meta:
		table_name = 'api_keys'

class AssayParams(BaseModel):
	assay = ForeignKeyField(column_name='assay_id', field='id', model=Assays)
	name = CharField()
	value = FloatField()

	class Meta:
		table_name = 'assay_params'
		indexes = (
			(('name', 'assay'), True),
		)

class AssayPositions(BaseModel):
	assay = ForeignKeyField(column_name='assay_id', field='id', model=Assays)
	battery = ForeignKeyField(column_name='battery_id', field='id', model=Batteries)
	start = IntegerField(index=True)

	class Meta:
		table_name = 'assay_positions'
		indexes = (
			(('battery', 'assay', 'start'), True),
		)

class AudioFiles(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users, null=True)
	data = BlobField()  # auto-corrected to BlobField
	filename = CharField(unique=True)
	n_seconds = FloatField()
	notes = CharField(null=True)
	sha1 = BlobField(unique=True)  # auto-corrected to BlobField

	class Meta:
		table_name = 'audio_files'

class Locations(BaseModel):
	active = IntegerField(constraints=[SQL("DEFAULT 1")])
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(constraints=[SQL("DEFAULT ''")])
	name = CharField(unique=True)
	part_of = ForeignKeyField(column_name='part_of', field='id', model='self', null=True)
	purpose = CharField(constraints=[SQL("DEFAULT ''")])
	temporary = IntegerField(constraints=[SQL("DEFAULT 0")])

	class Meta:
		table_name = 'locations'

class Refs(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_downloaded = DateTimeField(null=True)
	description = CharField(null=True)
	external_version = CharField(null=True)
	name = CharField(index=True)
	url = CharField(index=True, null=True)

	class Meta:
		table_name = 'refs'
		indexes = (
			(('name', 'external_version'), True),
		)

class Compounds(BaseModel):
	chembl = CharField(column_name='chembl_id', index=True, null=True)
	chemspider = IntegerField(column_name='chemspider_id', null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	inchi = CharField()
	inchikey = CharField(unique=True)
	inchikey_connectivity = CharField(index=True)
	smiles = CharField(null=True)

	class Meta:
		table_name = 'compounds'

class Batches(BaseModel):
	amount = CharField(null=True)
	box_number = IntegerField(index=True, null=True)
	compound = ForeignKeyField(column_name='compound_id', field='id', model=Compounds, null=True)
	concentration_millimolar = FloatField(null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	date_ordered = DateField(index=True, null=True)
	legacy_internal = CharField(column_name='legacy_internal_id', index=True, null=True)
	location = ForeignKeyField(column_name='location_id', field='id', model=Locations, null=True)
	location_note = CharField(null=True)
	lookup_hash = CharField(unique=True)
	made_from = ForeignKeyField(column_name='made_from_id', field='id', model='self', null=True)
	molecular_weight = FloatField(null=True)
	notes = TextField(null=True)
	person_ordered = ForeignKeyField(column_name='person_ordered', field='id', model=Users, null=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs, null=True)
	solvent = ForeignKeyField(backref='compounds_solvent_set', column_name='solvent_id', field='id', model=Compounds, null=True)
	supplier_catalog_number = CharField(null=True)
	supplier = ForeignKeyField(column_name='supplier_id', field='id', model=Suppliers, null=True)
	suspicious = IntegerField(constraints=[SQL("DEFAULT 0")])
	tag = CharField(null=True, unique=True)
	well_number = IntegerField(index=True, null=True)

	class Meta:
		table_name = 'batches'
		indexes = (
			(('box_number', 'well_number'), True),
		)

class BatchLabels(BaseModel):
	batch = ForeignKeyField(column_name='batch_id', field='id', model=Batches)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField(index=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'batch_labels'

class BiomarkerExperiments(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_collected = DateTimeField()
	datetime_prepared = DateTimeField()
	description = CharField()
	experimentalist = ForeignKeyField(column_name='experimentalist_id', field='id', model=Users)
	kind = CharField()
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)
	tag = CharField(unique=True)

	class Meta:
		table_name = 'biomarker_experiments'

class Genes(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	name = CharField(index=True, null=True)
	pub_link = CharField(index=True, null=True)
	sequence = TextField(null=True)

	class Meta:
		table_name = 'genes'

class Biomarkers(BaseModel):
	is_gene = ForeignKeyField(column_name='is_gene_id', field='id', model=Genes, null=True)
	name = CharField()
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'biomarkers'

class BiomarkerSamples(BaseModel):
	control_type = ForeignKeyField(column_name='control_type_id', field='id', model=ControlTypes)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	experiment = ForeignKeyField(column_name='experiment_id', field='id', model=BiomarkerExperiments)
	from_well = ForeignKeyField(column_name='from_well_id', field='id', model=Wells, null=True)
	name = CharField()

	class Meta:
		table_name = 'biomarker_samples'
		indexes = (
			(('name', 'experiment'), True),
		)

class BiomarkerLevels(BaseModel):
	biomarker = ForeignKeyField(column_name='biomarker_id', field='id', model=Biomarkers)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	fold_change = FloatField(null=True)
	full_value = CharField()
	sample = ForeignKeyField(column_name='sample_id', field='id', model=BiomarkerSamples)

	class Meta:
		table_name = 'biomarker_levels'

class BiomarkerTreatments(BaseModel):
	batch = ForeignKeyField(column_name='batch_id', field='id', model=Batches)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	micromolar_dose = FloatField()
	sample = ForeignKeyField(column_name='sample_id', field='id', model=BiomarkerSamples)

	class Meta:
		table_name = 'biomarker_treatments'
		indexes = (
			(('sample', 'batch'), True),
		)

class CarpProjectTypes(BaseModel):
	base_type = CharField()
	description = TextField(null=True)
	name = CharField(unique=True)

	class Meta:
		table_name = 'carp_project_types'

class CarpProjects(BaseModel):
	ancestor = ForeignKeyField(column_name='ancestor_id', field='id', model='self', null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = TextField(null=True)
	modified = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField(unique=True)
	owner = ForeignKeyField(column_name='owner_id', field='id', model=Users, null=True)
	project_type = ForeignKeyField(column_name='project_type_id', field='id', model=CarpProjectTypes)

	class Meta:
		table_name = 'carp_projects'

class CarpTankTypes(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField()
	name = CharField(unique=True)
	project_type = ForeignKeyField(column_name='project_type_id', field='id', model=CarpProjectTypes)

	class Meta:
		table_name = 'carp_tank_types'

class CarpTanks(BaseModel):
	alive = IntegerField(constraints=[SQL("DEFAULT 1")])
	birthdate = DateField(index=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	internal = CharField(column_name='internal_id', unique=True)
	notes = TextField(null=True)
	project = ForeignKeyField(column_name='project_id', field='id', model=CarpProjects)
	tank_type = ForeignKeyField(column_name='tank_type_id', field='id', model=CarpTankTypes)
	variant = ForeignKeyField(column_name='variant_id', field='id', model=GeneticVariants)

	class Meta:
		table_name = 'carp_tanks'

class CarpScans(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_scanned = DateTimeField(index=True)
	person_scanned = ForeignKeyField(column_name='person_scanned_id', field='id', model=Users)
	scan_type = CharField(index=True)
	scan_value = CharField(constraints=[SQL("DEFAULT ''")], index=True)
	tank = ForeignKeyField(column_name='tank_id', field='id', model=CarpTanks)

	class Meta:
		table_name = 'carp_scans'
		indexes = (
			(('tank', 'scan_type', 'datetime_scanned'), True),
		)

class CarpSystemData(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_scanned = DateTimeField()
	name = CharField()
	value = CharField()

	class Meta:
		table_name = 'carp_system_data'
		indexes = (
			(('name', 'datetime_scanned'), True),
		)

class CarpTasks(BaseModel):
	description = TextField(null=True)
	failure_condition = CharField(null=True)
	failure_target = ForeignKeyField(column_name='failure_target_id', field='id', model='self', null=True)
	min_age_days = IntegerField(null=True)
	name = CharField(index=True)
	notes = TextField(null=True)
	project_type = ForeignKeyField(column_name='project_type', field='id', model=CarpProjectTypes)
	success_condition = CharField(null=True)
	success_target = ForeignKeyField(backref='carp_tasks_success_target_set', column_name='success_target_id', field='id', model='self', null=True)
	tank_type = ForeignKeyField(column_name='tank_type_id', field='id', model=CarpTankTypes)

	class Meta:
		table_name = 'carp_tasks'
		indexes = (
			(('name', 'project_type'), True),
		)

class CarpTankTasks(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	notes = CharField(constraints=[SQL("DEFAULT ''")])
	tank = ForeignKeyField(column_name='tank_id', field='id', model=CarpTanks)
	task = ForeignKeyField(column_name='task_id', field='id', model=CarpTasks)

	class Meta:
		table_name = 'carp_tank_tasks'

class Sensors(BaseModel):
	blob_type = CharField(null=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	data_type = CharField()
	description = CharField(null=True)
	n_between = IntegerField(null=True)
	name = CharField(unique=True)

	class Meta:
		table_name = 'sensors'

class Stimuli(BaseModel):
	analog = IntegerField(constraints=[SQL("DEFAULT 0")])
	audio_file = ForeignKeyField(column_name='audio_file_id', field='id', model=AudioFiles, null=True, unique=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	default_color = CharField()
	description = CharField(null=True)
	name = CharField(unique=True)
	rgb = BlobField(null=True)  # auto-corrected to BlobField
	wavelength_nm = IntegerField(null=True)

	class Meta:
		table_name = 'stimuli'

class ComponentChecks(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	data = BlobField(null=True)  # auto-corrected to BlobField
	datetime_scanned = DateTimeField()
	name = CharField()
	sauron_config = ForeignKeyField(column_name='sauron_config_id', field='id', model=SauronConfigs)
	sensor = ForeignKeyField(column_name='sensor_id', field='id', model=Sensors)
	stimulus = ForeignKeyField(column_name='stimulus_id', field='id', model=Stimuli, null=True)
	value = CharField(null=True)

	class Meta:
		table_name = 'component_checks'

class CompoundLabels(BaseModel):
	compound = ForeignKeyField(column_name='compound_id', field='id', model=Compounds)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField()
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'compound_labels'

class Features(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	data_type = CharField(constraints=[SQL("DEFAULT 'float'")])
	description = CharField()
	dimensions = CharField()
	name = CharField(unique=True)

	class Meta:
		table_name = 'features'

class GeneLabels(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	gene = ForeignKeyField(column_name='gene_id', field='id', model=Genes)
	name = CharField(index=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'gene_labels'
		indexes = (
			(('gene', 'name', 'ref'), True),
		)

class GeneticConstructs(BaseModel):
	bacterial_strain = CharField(index=True, null=True)
	box_number = IntegerField(index=True)
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	creator = ForeignKeyField(column_name='creator_id', field='id', model=Users)
	date_made = DateTimeField(index=True, null=True)
	description = CharField()
	kind = CharField(index=True)
	location = ForeignKeyField(column_name='location_id', field='id', model=Locations, null=True)
	name = CharField(unique=True)
	notes = TextField(null=True)
	pmid = CharField(index=True, null=True)
	pub_link = CharField(null=True)
	raw_file = BlobField(null=True)  # auto-corrected to BlobField
	raw_file_sha1 = BlobField(null=True, unique=True)  # auto-corrected to BlobField
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)
	selection_marker = CharField(null=True)
	supplier = ForeignKeyField(column_name='supplier_id', field='id', model=Suppliers, null=True)
	tube_number = IntegerField(index=True)
	vector = CharField(index=True, null=True)

	class Meta:
		table_name = 'genetic_constructs'
		indexes = (
			(('box_number', 'tube_number'), True),
		)

class GeneticConstructFeatures(BaseModel):
	construct = ForeignKeyField(column_name='construct_id', field='id', model=GeneticConstructs)
	end = BigIntegerField(null=True)
	gene = ForeignKeyField(column_name='gene_id', field='id', model=Genes, null=True)
	is_complement = IntegerField(null=True)
	kind = CharField()
	name = CharField()
	start = BigIntegerField(null=True)

	class Meta:
		table_name = 'genetic_construct_features'
		indexes = (
			(('gene', 'construct'), True),
		)

class GeneticEvents(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	description = CharField(null=True)
	endogenous_gene = ForeignKeyField(column_name='endogenous_gene_id', field='id', model=Genes, null=True)
	endogenous_gene_position = IntegerField(null=True)
	injection_mix = CharField(null=True)
	on_reverse_strand = IntegerField(null=True)
	user = ForeignKeyField(column_name='user_id', field='id', model=Users)
	variant = ForeignKeyField(column_name='variant_id', field='id', model=GeneticVariants, null=True)

	class Meta:
		table_name = 'genetic_events'

class GeneticKnockins(BaseModel):
	event = ForeignKeyField(column_name='event_id', field='id', model=GeneticEvents)
	gene = ForeignKeyField(column_name='gene_id', field='id', model=Genes)

	class Meta:
		table_name = 'genetic_knockins'
		indexes = (
			(('gene', 'event'), True),
		)

class KaleWeights(BaseModel):
	description = TextField(null=True)
	floats = BlobField()  # auto-corrected to BlobField
	name = CharField(unique=True)
	project = ForeignKeyField(column_name='project_id', field='id', model=Superprojects)

	class Meta:
		table_name = 'kale_weights'

class LogFiles(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	run = ForeignKeyField(column_name='run_id', field='id', model=Runs)
	text = TextField()
	text_sha1 = BlobField(index=True)  # auto-corrected to BlobField

	class Meta:
		table_name = 'log_files'

class MandosInfo(BaseModel):
	compound = IntegerField(column_name='compound_id')
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField(index=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)
	value = CharField(index=True)

	class Meta:
		table_name = 'mandos_info'
		indexes = (
			(('name', 'ref', 'compound'), True),
		)

class MandosObjects(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	external = CharField(column_name='external_id', index=True)
	name = CharField(null=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'mandos_objects'
		indexes = (
			(('ref', 'external'), True),
		)

class MandosObjectTags(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField()
	object = ForeignKeyField(column_name='object', field='id', model=MandosObjects)
	ref = ForeignKeyField(column_name='ref', field='id', model=Refs)
	value = CharField(index=True)

	class Meta:
		table_name = 'mandos_object_tags'
		indexes = (
			(('object', 'ref', 'name', 'value'), True),
		)

class MandosPredicates(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	external = CharField(column_name='external_id', index=True, null=True)
	kind = CharField()
	name = CharField(index=True)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'mandos_predicates'
		indexes = (
			(('external', 'ref'), True),
			(('name', 'ref'), True),
		)

class MandosRules(BaseModel):
	compound = ForeignKeyField(column_name='compound_id', field='id', model=Compounds)
	external = CharField(column_name='external_id', index=True, null=True)
	object = ForeignKeyField(column_name='object_id', field='id', model=MandosObjects)
	predicate = ForeignKeyField(column_name='predicate_id', field='id', model=MandosPredicates)
	ref = ForeignKeyField(column_name='ref_id', field='id', model=Refs)

	class Meta:
		table_name = 'mandos_rules'
		indexes = (
			(('ref', 'compound', 'object', 'predicate'), True),
		)

class MandosRuleTags(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField()
	ref = ForeignKeyField(column_name='ref', field='id', model=Refs)
	rule = ForeignKeyField(column_name='rule', field='id', model=MandosRules)
	value = CharField(index=True)

	class Meta:
		table_name = 'mandos_rule_tags'
		indexes = (
			(('rule', 'ref', 'name', 'value'), True),
		)

class Rois(BaseModel):
	ref = IntegerField(column_name='ref_id', index=True)
	well = ForeignKeyField(column_name='well_id', field='id', model=Wells)
	x0 = IntegerField()
	x1 = IntegerField()
	y0 = IntegerField()
	y1 = IntegerField()

	class Meta:
		table_name = 'rois'

class RunTags(BaseModel):
	name = CharField()
	run = ForeignKeyField(column_name='run_id', field='id', model=Runs)
	value = CharField()

	class Meta:
		table_name = 'run_tags'
		indexes = (
			(('run', 'name'), True),
		)

class SauronSettings(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	name = CharField(index=True)
	sauron = ForeignKeyField(column_name='sauron', field='id', model=Saurons)
	value = CharField()

	class Meta:
		table_name = 'sauron_settings'
		indexes = (
			(('sauron', 'name'), True),
		)

class SensorData(BaseModel):
	floats = BlobField()  # auto-corrected to BlobField
	floats_sha1 = BlobField(index=True)  # auto-corrected to BlobField
	run = ForeignKeyField(column_name='run_id', field='id', model=Runs)
	sensor = ForeignKeyField(column_name='sensor_id', field='id', model=Sensors)

	class Meta:
		table_name = 'sensor_data'

class StimulusFrames(BaseModel):
	assay = ForeignKeyField(column_name='assay_id', field='id', model=Assays)
	frames = BlobField()  # auto-corrected to BlobField
	frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
	stimulus = ForeignKeyField(column_name='stimulus_id', field='id', model=Stimuli)

	class Meta:
		table_name = 'stimulus_frames'
		indexes = (
			(('assay', 'stimulus'), True),
		)

class SubmissionParams(BaseModel):
	name = CharField()
	param_type = CharField()
	submission = ForeignKeyField(column_name='submission_id', field='id', model=Submissions)
	value = CharField()

	class Meta:
		table_name = 'submission_params'
		indexes = (
			(('submission', 'name'), True),
		)

class SubmissionRecords(BaseModel):
	created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
	datetime_modified = DateTimeField()
	sauron = ForeignKeyField(column_name='sauron_id', field='id', model=Saurons)
	status = CharField(null=True)
	submission = ForeignKeyField(column_name='submission_id', field='id', model=Submissions)

	class Meta:
		table_name = 'submission_records'
		indexes = (
			(('submission', 'status', 'datetime_modified'), True),
		)

class TemplateStimulusFrames(BaseModel):
	range_expression = CharField()
	stimulus = ForeignKeyField(column_name='stimulus_id', field='id', model=Stimuli)
	template_assay = ForeignKeyField(column_name='template_assay_id', field='id', model=TemplateAssays)
	value_expression = CharField()

	class Meta:
		table_name = 'template_stimulus_frames'

class TemplateTreatments(BaseModel):
	batch_expression = CharField()
	dose_expression = CharField()
	template_plate = ForeignKeyField(column_name='template_plate_id', field='id', model=TemplatePlates)
	well_range_expression = CharField()

	class Meta:
		table_name = 'template_treatments'

class TemplateWells(BaseModel):
	age_expression = CharField()
	control_type = ForeignKeyField(column_name='control_type', field='id', model=ControlTypes, null=True)
	group_expression = CharField()
	n_expression = CharField()
	template_plate = ForeignKeyField(column_name='template_plate_id', field='id', model=TemplatePlates)
	variant_expression = CharField()
	well_range_expression = CharField()

	class Meta:
		table_name = 'template_wells'

class WellFeatures(BaseModel):
	floats = BlobField()  # auto-corrected to BlobField
	sha1 = BlobField(index=True)  # auto-corrected to BlobField
	type = ForeignKeyField(column_name='type_id', field='id', model=Features)
	well = ForeignKeyField(column_name='well_id', field='id', model=Wells)

	class Meta:
		table_name = 'well_features'

class WellTreatments(BaseModel):
	batch = ForeignKeyField(column_name='batch_id', field='id', model=Batches)
	micromolar_dose = FloatField(null=True)
	well = ForeignKeyField(column_name='well_id', field='id', model=Wells)

	class Meta:
		table_name = 'well_treatments'
		indexes = (
			(('well', 'batch'), True),
		)

