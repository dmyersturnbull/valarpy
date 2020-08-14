import os
from collections import defaultdict
from datetime import datetime
from numbers import Integral
from pathlib import PurePath
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence
from typing import Tuple as Tup
from typing import Union

import pandas as pd
import peewee
from peewee import *

from valarpy.connection import GLOBAL_CONNECTION

database = GLOBAL_CONNECTION.peewee_database


class ValarLookupError(KeyError):
    pass


class ValarTableTypeError(TypeError):
    pass


# noinspection PyProtectedMember
class EnumField(peewee._StringField):  # pragma: no cover
    """
    A MySQL `ENUM` field type.
    """

    field_type = "ENUM"

    def __init__(self, max_length=255, *args, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def get_modifiers(self):
        return self.max_length and [self.max_length] or None


class BinaryField(BlobField):  # pragma: no cover
    """
    A MySQL constant-width `BINARY` field type.
    """

    field_type = "BINARY"

    def __init__(self, max_length=255, *args, **kwargs):
        super(BinaryField, self).__init__(args, kwargs)
        self.max_length = max_length


class UnknownField(object):  # pragma: no cover
    """
    A field type that was not recognized.
    """

    def __init__(self, *_, **__):
        pass


class TableDescriptionFrame(pd.DataFrame):
    """
    A Pandas DataFrame subclass that contains the columns:
        - keys name (str)
        - type (str)
        - length (int or None)
        - nullable (bool)
        - choices (set or list)
        - primary (bool)
        - unique (bool)
        - constraints (list of constraint objects)
    """

    pass


class BaseModel(Model):
    """
    A table model in Valar through Valarpy and peewee.
    Provides functions in additional to the normal peewee functions.
    """

    class Meta:
        database = database

    def get_data(self) -> Dict[str, Any]:
        """
        Example usage:
            >>> Users.get(Users.id == 1).get_data()  # {'id': 2, 'username': 'john', ...}
        :return: the value of every field (column value)
        """
        return self.__data__

    @property
    def sstring(self) -> str:
        """Short string of the ID. This can be overridden."""
        return "".join([c for c in self.__class__.__name__ if c.isupper()]).lower() + str(self.id)

    @property
    def _data(self) -> Dict[str, Any]:  # pragma: no cover
        """
        See `get_data`.
        """
        # for compatibility with peewee version 2 code
        return self.__data__

    @classmethod
    def get_desc_list(cls) -> List[Dict[str, str]]:
        """
        Returns:
        :return: 	A list the columns in this table, where each is a dictionary of:
                    - keys name (str)
                    - type (str)
                    - length (int or None)
                    - nullable (bool)
                    - choices (set or list)
                    - primary (bool)
                    - unique (bool)
                    - constraints (list of constraint objects)
        """
        return cls.__description()

    @classmethod
    def get_desc(cls) -> TableDescriptionFrame:
        """
        Gets a description of this table as a Pandas DataFrame.
        Example usage:
            >>> Users.get_desc()
        :return: 	A TableDescriptionFrame (Pandas DataFrame subclass) of the columns:
                    - keys name (str)
                    - type (str)
                    - length (int or None)
                    - nullable (bool)
                    - choices (set or list)
                    - primary (bool)
                    - unique (bool)
                    - constraints (list of constraint objects)
        """

        def _cfirst(dataframe: pd.DataFrame, col_seq) -> pd.DataFrame:
            if len(dataframe) == 0:  # will break otherwise
                return dataframe
            else:
                return dataframe[col_seq + [c for c in dataframe.columns if c not in col_seq]]

        # noinspection PyTypeChecker
        df = pd.DataFrame.from_dict(cls.__description())
        return TableDescriptionFrame(
            _cfirst(df, ["name", "type", "nullable", "choices", "primary", "unique"])
        )

    @classmethod
    def get_schema(cls) -> str:
        """
        :return: A string that is **approximately** the text returned by the SQL `SHOW CREATE TABLE tablename`
        """
        return ",\n".join(
            [
                " ".join(
                    [
                        d["name"],
                        d["type"] + (str(d["choices"]) if d["choices"] is not None else ""),
                        ("NULL" if d["nullable"] else "NOT NULL"),
                        ("PRIMARY KEY" if d["primary"] else ("UNIQUE" if d["unique"] else "")),
                    ]
                ).rstrip()
                for d in cls.__description()
            ]
        )

    @classmethod
    def __description(cls) -> List[Dict[str, str]]:  # pragma: no cover
        """
        See `get_description`.
        """
        return [
            {
                "name": v.name,
                "type": v.field_type,
                "nullable": v.null,
                "choices": v.choices if hasattr(v, "choices") else None,
                "primary": v.primary_key,
                "unique": v.unique,
                "constraints": 0 if v.constraints is None else len(v.constraints),
            }
            for k, v in cls._meta.fields.items()
        ]

    @classmethod
    def list_where(cls, *wheres: Sequence[peewee.Expression], **values: Mapping[str, Any]):
        query = cls.select()
        for where in wheres:
            query = query.where(where)
        for name, value in values.items():
            query = query.where(getattr(cls, name) == value)
        return list(query)

    @classmethod
    def fetch_or_none(
        cls, thing: Union[Integral, str, peewee.Model], like: bool = False, regex: bool = False
    ) -> Optional[peewee.Model]:
        """
        Gets the first (which is unique) match of the row by:
            -   instance of this class (just returns it)
            -   `id` columns (if `thing` is an integer-like type
            -   any of this class's unique string columns;
                more specifically, a column that is marked in SQL as both (`VARCHAR`, `CHAR`, or `ENUM`) and `UNIQUE`
        Also see `fetch`, which raises an error if then row was not found.
        Example usage:
            >>> # assuming John has ID 2
            >>> user = Users.fetch('john')
            >>> print(user)  # Users(2)
        :param thing: A string, int that
        :param like: Use a LIKE expression and wrap in % %
        :param regex: Treat ``thing`` as a regex pattern
        :return: The Peewee row instance that was found OR None if it does not exist
        :raises ValarTableTypeError: If `thing` is an instance of BaseModel of the wrong type (not this class)
        :raises TypeError: If `thing` was not a str, int-like, or a BaseModel
        """
        if isinstance(thing, cls):
            return thing
        elif isinstance(thing, peewee.Model):
            raise ValarTableTypeError(
                "Fetching a {} on class {}".format(thing.__class__.__name__, cls.__name__)
            )
        elif isinstance(thing, Integral) or isinstance(thing, float):
            # noinspection PyUnresolvedReferences
            return cls.get_or_none(cls.id == int(thing))
        elif isinstance(thing, str) and len(cls.__indexing_cols()) > 0:
            return cls.get_or_none(cls._build_or_query([thing], like=like, regex=regex))
        else:
            raise TypeError(
                "Fetching with unknown type {} on class {}".format(
                    thing.__class__.__name__, cls.__name__
                )
            )

    @classmethod
    def fetch(
        cls, thing: Union[Integral, str, peewee.Model], like: bool = False, regex: bool = False
    ) -> peewee.Model:
        """
        Gets the first (which is unique) match of the row by:
            -   instance of this class (just returns it)
            -   `id` columns (if `thing` is an integer-like type
            -   any of this class's unique string columns;
                more specifically, a column that is marked in SQL as both (`VARCHAR`, `CHAR`, or `ENUM`) and `UNIQUE`
        Also see `fetch_or_none`, which returns None if the row was not found
        Example usage:
            >>> # assuming John has ID 2
            >>> user = Users.fetch('john')
            >>> print(user)  # Users(2)
        :param thing: A string, int that
        :param like: Use a LIKE expression and wrap in % %
        :param regex: Treat ``thing`` as a regex pattern
        :return: The Peewee row instance that was found
        :raises A ValarLookupError If the row was not found
        :raises ValarTableTypeError: If `thing` is an instance of BaseModel of the wrong type (not this class)
        :raises TypeError: If `thing` was not a str, int-like, or a BaseModel
        """
        found = cls.fetch_or_none(thing, like=like, regex=regex)
        if found is None:
            raise ValarLookupError("Could not find {} in {}".format(thing, cls))
        return found

    @classmethod
    def fetch_all(
        cls, things: Iterable[Union[Integral, str, peewee.Model]]
    ) -> Sequence[peewee.Model]:
        """
            Fetches rows corresponding to `things` from their instances, IDs, or values from unique columns.
            See `fetch` for full information.
            Also see `fetch_all_or_none` for a similar function.
            This method is preferrable to calling `fetch` repeatedly because it minimizes the number of queries.
            Specifically, it will perform 0, 1, or 2 queries depending on the passed types:
                - If only instances are passed, it just returns them (0 queries)
                - If only IDs or only string values are passed, it performs 1 query
                - If both IDs and string values are passed, it performs 2 queries
            Example usage:
                >>> # assuming John has ID 2 and Alex has user ID 14
                >>> users = Users.fetch_all(['john', 14, 'john', Users.get(Users.id == 2)])
                >>> print(users)  # [Users(2), Users(14), Users(2), Users(2)]
            :return: A sequence of the rows found, in the same order as they were passed
            :raises ValarLookupError: If any of the elements of `things` was not found
            :raises ValarTableTypeError: If an instance of a BaseModel of the wrong type (not this class) was passed
            :raises TypeError: If the type of an element was otherwise invalid (not str, BaseModel, or int-like)
        """

        def _x(thing):  # pragma: no cover
            if thing is None:
                raise ValarLookupError("Could not find {} in {}".format(thing, cls))
            return thing

        return [_x(thing) for thing in cls.fetch_all_or_none(things)]

    @classmethod
    def fetch_all_or_none(
        cls,
        things: Iterable[Union[Integral, str, peewee.Model]],
        join_fn: Optional[Callable[[peewee.Expression], peewee.Expression]] = None,
    ) -> Iterable[peewee.Model]:
        """
            Fetches rows corresponding to `things` from their instances, IDs, or values from unique columns.
            See `fetch` for full information.
            Also see `fetch_all` for a similar function.
            This method is preferrable to calling `fetch` repeatedly because it minimizes the number of queries.
            Specifically, it will perform 0, 1, or 2 queries depending on the passed types:
                - If only instances are passed, it just returns them (0 queries)
                - If only IDs or only string values are passed, it performs 1 query
                - If both IDs and string values are passed, it performs 2 queries
            Example usage:
                >>> # assuming John has ID 2 and Alex has user ID 14
                >>> users = Users.fetch_all_or_none(['john', 14, 'john', Users.get(Users.id == 2)])
                >>> print(users)  # [Users(2), Users(14), Users(2), Users(2)]
            :return: A sequence of the rows found, or None if they were not found; in the same order as they were passed
            :raises ValarTableTypeError: If an instance of a BaseModel of the wrong type (not this class) was passed
            :raises TypeError: If the type of an element was otherwise invalid (not str, BaseModel, or int-like)
        """
        # modify arguments
        things = list(things)
        has_join_fn = join_fn is not None
        if join_fn is None:

            def join_fn(s):
                return s

        # handle errors
        bad_models = [
            isinstance(thing, peewee.Model) and not isinstance(thing, cls) for thing in things
        ]
        if any(bad_models):
            raise ValarTableTypeError(
                "Fetching a {} on invalid classes {}".format(cls.__name__, set(bad_models))
            )
        bad_types = [not isinstance(thing, (cls, Integral, str)) for thing in things]
        if any(bad_types):
            raise TypeError(
                "Fetching a {} on unknown types {}".format(cls.__name__, set(bad_types))
            )
        # utility functions
        def do_q():
            return join_fn(cls.select())

        def make_dct(the_type):
            dct = defaultdict(list)
            for i, thing in enumerate(things):
                if isinstance(thing, the_type):
                    dct[thing].append(i)
            return dct

        # now we fetch
        # this will become a dict mapping every index in things to its instance
        index_to_match = {}
        # first, we can add all of the actual instances
        # if we need to join on other tables, we'll to do queries anyway
        model_things = make_dct(cls)
        if has_join_fn and len(model_things) > 0:
            for match in do_q().where(cls.id << [z.id for z in model_things.keys()]):
                for ind in model_things[match]:
                    index_to_match[ind] = match
        elif len(model_things) > 0:
            for thing in model_things:
                for ind in model_things[thing]:
                    index_to_match[ind] = thing
        # now let's collect those that are ints and those that are strs
        # unfortunately right now we have to do 2 queries (ID and names), or we'll get type a mismatch error
        int_things = make_dct(Integral)
        str_things = make_dct(str)
        if len(int_things) > 0:
            for match in do_q().where(cls.id << {int(t) for t, ilist in int_things.items()}):
                for ind in int_things[match.id]:
                    index_to_match[ind] = match
        if len(str_things) > 0:
            for match in do_q().where(cls._build_or_query(list(set(str_things.keys())))):
                for col in cls.__indexing_cols():
                    my_attr = getattr(match, col)
                    if my_attr in str_things:
                        for ind in str_things[my_attr]:
                            index_to_match[ind] = match
        return [index_to_match.get(i, None) for i in range(0, len(things))]

    @classmethod
    def fetch_to_query(
        cls,
        thing: Union[
            Integral,
            str,
            peewee.Model,
            peewee.Expression,
            Sequence[peewee.Expression],
            Sequence[Union[Integral, str, peewee.Model]],
        ],
    ) -> Sequence[peewee.Expression]:
        """
        This method has limited but important reasons for being called.
        See `fetch`, `fetch_or_none`, `fetch_all`, or `fetch_all_or_none` for more commonly used functions.
        Returns a sequence of Peewee expressions corresponding to WHERE statements:
            - If the instance is one of (int, str, or model), that the row is the one passed, matched by ID or unique column value as needed
            - If the instance is a Peewee expression itself, that the expression matches
        :raises ValarTableTypeError: If `thing` is an instance of BaseModel of the wrong type (not this class)
        :param thing: An int-type to be looked up by the `id` column, a `str` to be looked up by an of:
                - a unique column value
                - a model instance
                - an expression
                - a list of expressions
        :return A sequence of Peewee expressions to be joined with AND
        :raises TypeError: If `thing` was not a str, int-like, or a BaseModel
        """
        if isinstance(thing, (Integral, str, Model, peewee.Expression)):
            thing = [thing]
        if all(isinstance(t, peewee.Expression) for t in thing):
            return thing
        elif all(isinstance(t, (Integral, str, Model)) for t in thing):
            # noinspection PyTypeChecker,PyUnresolvedReferences
            return [cls.id << {x.id for x in cls.fetch_all_or_none(thing) if x is not None}]
        raise TypeError("Invalid type for {} in {}".format(thing, cls))

    @classmethod
    def _build_or_query(
        cls, values: Sequence[Union[Model, int, str]], like: bool = False, regex: bool = False
    ) -> Optional[peewee.Expression]:  # pragma: no cover
        assert not (like and regex)
        cols = list(cls.__indexing_cols())
        if len(values) == 0:
            return None
        ids = [i for i in values if isinstance(i, int)]
        ids.extend([i.id for i in values if isinstance(i, cls)])
        strs = [i for i in values if isinstance(i, str)]
        ors = [cls.id << ids]
        if like:
            ors.extend((cls.__gen_ors(strs, cols, lambda attr, t: attr % ("%" + t + "%"))))
        elif regex:
            ors.extend(cls.__gen_ors(strs, cols, lambda attr, t: attr.regexp(t)))
        else:
            ors.extend([getattr(cls, col) << strs for col in cols])
        return cls.__ors_to_query(ors)

    @classmethod
    def __gen_ors(cls, things, cols, function):  # pragma: no cover
        for thing in things:
            for col in cols:
                yield function(getattr(cls, col), thing)

    @classmethod
    def __ors_to_query(cls, ors):  # pragma: no cover
        assert len(ors) > 0
        query = ors[0]
        for e in ors[1:]:
            query = query | e
        return query

    @classmethod
    def __indexing_cols(cls):  # pragma: no cover
        return {
            k
            for k, v in cls._meta.fields.items()
            if v.unique and v.field_type in {"VARCHAR", "CHAR", "ENUM"}
        }

    @classmethod
    def get_indexing_cols(cls):  # pragma: no cover
        return cls.__indexing_cols()


class Suppliers(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "suppliers"


class PlateTypes(BaseModel):  # pragma: no cover
    n_columns = IntegerField()
    n_rows = IntegerField()
    name = CharField(null=True)
    opacity = EnumField(choices=("opaque", "transparent"))  # auto-corrected to Enum
    part_number = CharField(index=True, null=True)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=Suppliers, null=True)
    well_shape = EnumField(choices=("round", "square", "rectangular"))  # auto-corrected to Enum

    class Meta:
        table_name = "plate_types"
        indexes = ((("n_rows", "n_columns"), False),)


class Users(BaseModel):  # pragma: no cover
    bcrypt_hash = CharField(index=True, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    first_name = CharField(index=True)
    last_name = CharField(index=True)
    username = CharField(unique=True)
    write_access = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)

    class Meta:
        table_name = "users"


class Plates(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_plated = DateTimeField(index=True, null=True)
    person_plated = ForeignKeyField(column_name="person_plated_id", field="id", model=Users)
    plate_type = ForeignKeyField(
        column_name="plate_type_id", field="id", model=PlateTypes, null=True
    )

    class Meta:
        table_name = "plates"


class TransferPlates(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users)
    datetime_created = DateTimeField()
    description = CharField(null=True)
    dilution_factor_from_parent = FloatField(null=True)
    initial_ul_per_well = FloatField()
    name = CharField(unique=True)
    parent = ForeignKeyField(column_name="parent_id", field="id", model="self", null=True)
    plate_type = ForeignKeyField(column_name="plate_type_id", field="id", model=PlateTypes)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=Suppliers, null=True)

    class Meta:
        table_name = "transfer_plates"


class Batteries(BaseModel):  # pragma: no cover
    assays_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    author = ForeignKeyField(column_name="author_id", field="id", model=Users, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    length = IntegerField(index=True)
    name = CharField(unique=True)
    notes = CharField(null=True)
    template = IntegerField(column_name="template_id", index=True, null=True)

    class Meta:
        table_name = "batteries"


class ProjectTypes(BaseModel):  # pragma: no cover
    description = TextField()
    name = CharField(unique=True)

    class Meta:
        table_name = "project_types"


class Projects(BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users)
    description = CharField(null=True)
    methods = TextField(null=True)
    name = CharField(unique=True)
    reason = TextField(null=True)
    type = ForeignKeyField(column_name="type_id", field="id", model=ProjectTypes, null=True)

    class Meta:
        table_name = "superprojects"


class TemplatePlates(BaseModel):  # pragma: no cover
    author = ForeignKeyField(column_name="author_id", field="id", model=Users)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    name = CharField(unique=True)
    plate_type = ForeignKeyField(column_name="plate_type_id", field="id", model=PlateTypes)
    specializes = ForeignKeyField(column_name="specializes", field="id", model="self", null=True)

    class Meta:
        table_name = "template_plates"


class Experiments(BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    battery = ForeignKeyField(column_name="battery_id", field="id", model=Batteries)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users)
    default_acclimation_sec = IntegerField()
    description = CharField(null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    project = ForeignKeyField(column_name="project_id", field="id", model=Projects)
    template_plate = ForeignKeyField(
        column_name="template_plate_id", field="id", model=TemplatePlates, null=True
    )
    transfer_plate = ForeignKeyField(
        column_name="transfer_plate_id", field="id", model=TransferPlates, null=True
    )

    class Meta:
        table_name = "experiments"


class ExperimentTags(BaseModel):  # pragma: no cover
    name = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=Experiments)
    value = CharField()

    class Meta:
        table_name = "experiment_tags"
        indexes = ((("experiment", "name"), True),)


class Saurons(BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(unique=True)

    class Meta:
        table_name = "saurons"


class SauronConfigs(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_changed = DateTimeField()
    description = TextField()
    sauron = ForeignKeyField(column_name="sauron_id", field="id", model=Saurons)

    class Meta:
        table_name = "sauron_configs"
        indexes = ((("sauron", "datetime_changed"), True),)


class Submissions(BaseModel):  # pragma: no cover
    acclimation_sec = IntegerField(null=True)
    continuing = ForeignKeyField(column_name="continuing_id", field="id", model="self", null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_dosed = DateTimeField(null=True)
    datetime_plated = DateTimeField()
    description = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=Experiments)
    lookup_hash = CharField(unique=True)
    notes = TextField(null=True)
    person_plated = ForeignKeyField(column_name="person_plated_id", field="id", model=Users)
    user = ForeignKeyField(backref="users_user_set", column_name="user_id", field="id", model=Users)

    class Meta:
        table_name = "submissions"


class ConfigFiles(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    text_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    toml_text = TextField()

    class Meta:
        table_name = "config_files"


class Runs(BaseModel):  # pragma: no cover
    acclimation_sec = IntegerField(index=True, null=True)
    config_file = ForeignKeyField(
        column_name="config_file_id", field="id", model=ConfigFiles, null=True
    )
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_dosed = DateTimeField(index=True, null=True)
    datetime_run = DateTimeField(index=True)
    description = CharField()
    experiment = ForeignKeyField(column_name="experiment_id", field="id", model=Experiments)
    experimentalist = ForeignKeyField(column_name="experimentalist_id", field="id", model=Users)
    incubation_min = IntegerField(index=True, null=True)
    name = CharField(null=True, unique=True)
    notes = TextField(null=True)
    plate = ForeignKeyField(column_name="plate_id", field="id", model=Plates)
    sauron_config = ForeignKeyField(column_name="sauron_config_id", field="id", model=SauronConfigs)
    submission = ForeignKeyField(
        column_name="submission_id", field="id", model=Submissions, null=True, unique=True
    )
    tag = CharField(constraints=[SQL("DEFAULT ''")], unique=True)

    class Meta:
        table_name = "runs"


class TemplateAssays(BaseModel):  # pragma: no cover
    author = ForeignKeyField(column_name="author_id", field="id", model=Users, null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    name = CharField(unique=True)
    specializes = ForeignKeyField(column_name="specializes", field="id", model="self", null=True)

    class Meta:
        table_name = "template_assays"


class Assays(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(null=True)
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    hidden = IntegerField(constraints=[SQL("DEFAULT 0")])
    length = IntegerField()
    name = CharField(unique=True)
    template_assay = ForeignKeyField(
        column_name="template_assay_id", field="id", model=TemplateAssays, null=True
    )

    class Meta:
        table_name = "assays"
        indexes = ((("name", "frames_sha1"), True),)


class ControlTypes(BaseModel):  # pragma: no cover
    description = CharField()
    drug_related = IntegerField(constraints=[SQL("DEFAULT 1")], index=True)
    genetics_related = IntegerField(index=True)
    name = CharField(unique=True)
    positive = IntegerField(index=True)

    class Meta:
        table_name = "control_types"


class GeneticVariants(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users)
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


class Wells(BaseModel):  # pragma: no cover
    age = IntegerField(null=True)
    control_type = ForeignKeyField(
        column_name="control_type_id", field="id", model=ControlTypes, null=True
    )
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    n = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    run = ForeignKeyField(column_name="run_id", field="id", model=Runs)
    variant = ForeignKeyField(
        column_name="variant_id", field="id", model=GeneticVariants, null=True
    )
    well_group = CharField(index=True, null=True)
    well_index = IntegerField(index=True)

    class Meta:
        table_name = "wells"
        indexes = ((("run", "well_index"), True),)


class Annotations(BaseModel):  # pragma: no cover
    annotator = ForeignKeyField(column_name="annotator_id", field="id", model=Users)
    assay = ForeignKeyField(column_name="assay_id", field="id", model=Assays, null=True)
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
    run = ForeignKeyField(column_name="run_id", field="id", model=Runs, null=True)
    submission = ForeignKeyField(
        column_name="submission_id", field="id", model=Submissions, null=True
    )
    value = CharField(null=True)
    well = ForeignKeyField(column_name="well_id", field="id", model=Wells, null=True)

    class Meta:
        table_name = "annotations"


class AssayParams(BaseModel):  # pragma: no cover
    assay = ForeignKeyField(column_name="assay_id", field="id", model=Assays)
    name = CharField()
    value = FloatField()

    class Meta:
        table_name = "assay_params"
        indexes = ((("name", "assay"), True),)


class AssayPositions(BaseModel):  # pragma: no cover
    assay = ForeignKeyField(column_name="assay_id", field="id", model=Assays)
    battery = ForeignKeyField(column_name="battery_id", field="id", model=Batteries)
    start = IntegerField(index=True)

    class Meta:
        table_name = "assay_positions"
        indexes = ((("battery", "assay", "start"), True),)


class AudioFiles(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users, null=True)
    data = BlobField()  # auto-corrected to BlobField
    filename = CharField(unique=True)
    n_seconds = FloatField()
    notes = CharField(null=True)
    sha1 = BlobField(unique=True)  # auto-corrected to BlobField

    class Meta:
        table_name = "audio_files"


class Locations(BaseModel):  # pragma: no cover
    active = IntegerField(constraints=[SQL("DEFAULT 1")])
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    description = CharField(constraints=[SQL("DEFAULT ''")])
    name = CharField(unique=True)
    part_of = ForeignKeyField(column_name="part_of", field="id", model="self", null=True)
    purpose = CharField(constraints=[SQL("DEFAULT ''")])
    temporary = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = "locations"


class Refs(BaseModel):  # pragma: no cover
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


class Compounds(BaseModel):  # pragma: no cover
    chembl = CharField(column_name="chembl_id", index=True, null=True)
    chemspider = IntegerField(column_name="chemspider_id", null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    inchi = CharField()
    inchikey = CharField(unique=True)
    inchikey_connectivity = CharField(index=True)
    smiles = CharField(null=True)

    class Meta:
        table_name = "compounds"


class Batches(BaseModel):  # pragma: no cover
    amount = CharField(null=True)
    box_number = IntegerField(index=True, null=True)
    compound = ForeignKeyField(column_name="compound_id", field="id", model=Compounds, null=True)
    concentration_millimolar = FloatField(null=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    date_ordered = DateField(index=True, null=True)
    legacy_internal = CharField(column_name="legacy_internal_id", index=True, null=True)
    location = ForeignKeyField(column_name="location_id", field="id", model=Locations, null=True)
    location_note = CharField(null=True)
    lookup_hash = CharField(unique=True)
    made_from = ForeignKeyField(column_name="made_from_id", field="id", model="self", null=True)
    molecular_weight = FloatField(null=True)
    notes = TextField(null=True)
    person_ordered = ForeignKeyField(
        column_name="person_ordered", field="id", model=Users, null=True
    )
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs, null=True)
    solvent = IntegerField(column_name="solvent_id", index=True, null=True)
    # hide to make queries easier
    # solvent = ForeignKeyField(backref='compounds_solvent_set', column_name='solvent_id', field='id', model=Compounds, null=True)
    supplier_catalog_number = CharField(null=True)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=Suppliers, null=True)
    suspicious = IntegerField(constraints=[SQL("DEFAULT 0")])
    tag = CharField(null=True, unique=True)
    well_number = IntegerField(index=True, null=True)

    class Meta:
        table_name = "batches"
        indexes = ((("box_number", "well_number"), True),)


class BatchLabels(BaseModel):  # pragma: no cover
    batch = ForeignKeyField(column_name="batch_id", field="id", model=Batches)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(index=True)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "batch_labels"


class Sensors(BaseModel):  # pragma: no cover
    blob_type = EnumField(
        choices=(
            "assay_start",
            "protocol_start",
            "every_n_milliseconds",
            "every_n_frames",
            "arbitrary",
        ),
        null=True,
    )  # auto-corrected to Enum
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
            "long",
            "unsigned_long",
            "other",
        )
    )  # auto-corrected to Enum
    description = CharField(null=True)
    n_between = IntegerField(null=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "sensors"


class Stimuli(BaseModel):  # pragma: no cover
    analog = IntegerField(constraints=[SQL("DEFAULT 0")])
    audio_file = ForeignKeyField(
        column_name="audio_file_id", field="id", model=AudioFiles, null=True, unique=True
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


class CompoundLabels(BaseModel):  # pragma: no cover
    compound = ForeignKeyField(column_name="compound_id", field="id", model=Compounds)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField()
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "compound_labels"


class Features(BaseModel):  # pragma: no cover
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

    class Meta:
        table_name = "features"


class GeneticConstructs(BaseModel):  # pragma: no cover
    bacterial_strain = CharField(index=True, null=True)
    box_number = IntegerField(index=True)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    creator = ForeignKeyField(column_name="creator_id", field="id", model=Users)
    date_made = DateTimeField(index=True, null=True)
    description = CharField()
    kind = EnumField(
        choices=("plasmid", "guide", "morpholino", "other"), index=True
    )  # auto-corrected to Enum
    location = ForeignKeyField(column_name="location_id", field="id", model=Locations, null=True)
    name = CharField(unique=True)
    notes = TextField(null=True)
    pmid = CharField(index=True, null=True)
    pub_link = CharField(null=True)
    raw_file = BlobField(null=True)  # auto-corrected to BlobField
    raw_file_sha1 = BlobField(index=True, null=True)  # auto-corrected to BlobField
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)
    selection_marker = CharField(null=True)
    supplier = ForeignKeyField(column_name="supplier_id", field="id", model=Suppliers, null=True)
    tube_number = IntegerField(index=True)
    vector = CharField(index=True, null=True)

    class Meta:
        table_name = "genetic_constructs"
        indexes = ((("box_number", "tube_number"), True),)


class LogFiles(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    run = ForeignKeyField(column_name="run_id", field="id", model=Runs)
    text = TextField()
    text_sha1 = BlobField(index=True)  # auto-corrected to BlobField

    class Meta:
        table_name = "log_files"


class MandosInfo(BaseModel):  # pragma: no cover
    compound = ForeignKeyField(column_name="compound_id", field="id", model=Compounds)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(index=True)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)
    value = CharField(index=True)

    class Meta:
        table_name = "mandos_info"
        indexes = ((("name", "ref", "compound"), True),)


class MandosObjects(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    external = CharField(column_name="external_id", index=True)
    name = CharField(null=True)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "mandos_objects"
        indexes = ((("ref", "external_id"), True),)


class MandosObjectLinks(BaseModel):  # pragma: no cover
    child = ForeignKeyField(column_name="child_id", field="id", model=MandosObjects)
    parent = ForeignKeyField(
        backref="mandos_objects_parent_set",
        column_name="parent_id",
        field="id",
        model=MandosObjects,
    )
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "mandos_object_links"


class MandosObjectTags(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField()
    object = ForeignKeyField(column_name="object", field="id", model=MandosObjects)
    ref = ForeignKeyField(column_name="ref", field="id", model=Refs)
    value = CharField(index=True)

    class Meta:
        table_name = "mandos_object_tags"
        indexes = ((("object", "ref", "name", "value"), True),)


class MandosPredicates(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    external = CharField(column_name="external_id", index=True, null=True)
    kind = EnumField(choices=("target", "class", "indication", "other"))  # auto-corrected to Enum
    name = CharField(index=True)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "mandos_predicates"
        indexes = (
            (("external_id", "ref"), True),
            (("name", "ref"), True),
        )


class MandosRules(BaseModel):  # pragma: no cover
    compound = ForeignKeyField(column_name="compound_id", field="id", model=Compounds)
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    external = CharField(column_name="external_id", index=True, null=True)
    object = ForeignKeyField(column_name="object_id", field="id", model=MandosObjects)
    predicate = ForeignKeyField(column_name="predicate_id", field="id", model=MandosPredicates)
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)

    class Meta:
        table_name = "mandos_rules"
        indexes = ((("ref", "compound", "object", "predicate"), True),)


class MandosRuleTags(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField()
    ref = ForeignKeyField(column_name="ref", field="id", model=Refs)
    rule = ForeignKeyField(column_name="rule", field="id", model=MandosRules)
    value = CharField(index=True)

    class Meta:
        table_name = "mandos_rule_tags"
        indexes = ((("rule", "ref", "name", "value"), True),)


class Rois(BaseModel):  # pragma: no cover
    ref = ForeignKeyField(column_name="ref_id", field="id", model=Refs)
    well = ForeignKeyField(column_name="well_id", field="id", model=Wells)
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


class RunTags(BaseModel):  # pragma: no cover
    name = CharField()
    run = ForeignKeyField(column_name="run_id", field="id", model=Runs)
    value = CharField()

    class Meta:
        table_name = "run_tags"
        indexes = ((("run", "name"), True),)


class SauronSettings(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    name = CharField(index=True)
    sauron_config = ForeignKeyField(column_name="sauron_config_id", field="id", model=SauronConfigs)
    value = CharField()

    class Meta:
        table_name = "sauron_settings"
        indexes = ((("sauron_config", "name"), True),)


class SensorData(BaseModel):  # pragma: no cover
    floats = BlobField()  # auto-corrected to BlobField
    floats_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    run = ForeignKeyField(column_name="run_id", field="id", model=Runs)
    sensor = ForeignKeyField(column_name="sensor_id", field="id", model=Sensors)

    class Meta:
        table_name = "sensor_data"


class StimulusFrames(BaseModel):  # pragma: no cover
    assay = ForeignKeyField(column_name="assay_id", field="id", model=Assays)
    frames = BlobField()  # auto-corrected to BlobField
    frames_sha1 = BlobField(index=True)  # auto-corrected to BlobField
    stimulus = ForeignKeyField(column_name="stimulus_id", field="id", model=Stimuli)

    class Meta:
        table_name = "stimulus_frames"
        indexes = ((("assay", "stimulus"), True),)


class SubmissionParams(BaseModel):  # pragma: no cover
    name = CharField()
    param_type = EnumField(
        choices=("n_fish", "compound", "dose", "variant", "dpf", "group")
    )  # auto-corrected to Enum
    submission = ForeignKeyField(column_name="submission_id", field="id", model=Submissions)
    value = CharField()

    class Meta:
        table_name = "submission_params"
        indexes = ((("submission", "name"), True),)


class SubmissionRecords(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    datetime_modified = DateTimeField()
    sauron = ForeignKeyField(column_name="sauron_id", field="id", model=Saurons)
    status = EnumField(
        choices=(
            "starting",
            "capturing",
            "failed",
            "cancelled",
            "extracting",
            "compressing",
            "uploading",
            "uploaded",
            "inserting",
            "inserting features",
            "inserting sensors",
            "insert failed",
            "available",
            "failed_during_initialization",
            "failed_during_capture",
            "failed_during_postprocessing",
            "failed_during_upload",
            "cancelled_during_capture",
            "finished_capture",
        ),
        null=True,
    )  # auto-corrected to Enum
    submission = ForeignKeyField(column_name="submission_id", field="id", model=Submissions)

    class Meta:
        table_name = "submission_records"
        indexes = ((("submission", "status", "datetime_modified"), True),)


class TemplateStimulusFrames(BaseModel):  # pragma: no cover
    range_expression = CharField()
    stimulus = ForeignKeyField(column_name="stimulus_id", field="id", model=Stimuli)
    template_assay = ForeignKeyField(
        column_name="template_assay_id", field="id", model=TemplateAssays
    )
    value_expression = CharField()

    class Meta:
        table_name = "template_stimulus_frames"


class TemplateTreatments(BaseModel):  # pragma: no cover
    batch_expression = CharField()
    dose_expression = CharField()
    template_plate = ForeignKeyField(
        column_name="template_plate_id", field="id", model=TemplatePlates
    )
    well_range_expression = CharField()

    class Meta:
        table_name = "template_treatments"


class TemplateWells(BaseModel):  # pragma: no cover
    age_expression = CharField()
    control_type = ForeignKeyField(
        column_name="control_type", field="id", model=ControlTypes, null=True
    )
    group_expression = CharField()
    n_expression = CharField()
    template_plate = ForeignKeyField(
        column_name="template_plate_id", field="id", model=TemplatePlates
    )
    variant_expression = CharField()
    well_range_expression = CharField()

    class Meta:
        table_name = "template_wells"


class WellFeatures(BaseModel):  # pragma: no cover
    floats = BlobField()  # auto-corrected to BlobField
    sha1 = BlobField(index=True)  # auto-corrected to BlobField
    type = ForeignKeyField(column_name="type_id", field="id", model=Features)
    well = ForeignKeyField(column_name="well_id", field="id", model=Wells)

    class Meta:
        table_name = "well_features"


class WellTreatments(BaseModel):  # pragma: no cover
    batch = ForeignKeyField(column_name="batch_id", field="id", model=Batches)
    micromolar_dose = FloatField(null=True)
    well = ForeignKeyField(column_name="well_id", field="id", model=Wells)

    class Meta:
        table_name = "well_treatments"
        indexes = ((("well", "batch"), True),)


class BatchAnnotations(BaseModel):  # pragma: no cover
    annotator = ForeignKeyField(column_name="annotator_id", field="id", model=Users)
    batch = ForeignKeyField(column_name="batch_id", field="id", model=Batches, null=False)
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


class DagsToCreate(BaseModel):  # pragma: no cover
    created = DateTimeField(constraints=[SQL("DEFAULT current_timestamp()")])
    dag_created = IntegerField(constraints=[SQL("DEFAULT 0")])
    feature_type = ForeignKeyField(
        column_name="feature_type", field="id", model=Features, null=True
    )
    submission_hash = CharField()

    class Meta:
        table_name = "dags_to_create"
        indexes = ((("submission_hash", "feature_type"), True),)


ExpressionLike = peewee.ColumnBase
ExpressionsLike = Union[ExpressionLike, Iterable[ExpressionLike]]
PLike = Union[str, PurePath, os.PathLike]
RunLike = Union[int, str, Runs, Submissions]
ControlLike = Union[int, str, ControlTypes]
SubmissionLike = Union[int, str, Submissions]
RoiLike = Union[int, Rois, Tup[Union[int, str, Wells], Union[int, str, Refs]]]
RunsLike = Union[RunLike, Iterable[RunLike]]
SauronLike = Union[int, str, Saurons]
SauronConfigLike = Union[int, SauronConfigs, Tup[Union[Saurons, int, str], datetime]]
BatteryLike = Union[int, str, Batteries]
AssayLike = Union[int, str, Assays]
UserLike = Union[int, str, Users]
RefLike = Union[int, str, Refs]
TempPlateLike = Union[int, str, TemplatePlates]
SupplierLike = Union[int, str, Suppliers]
BatchLike = Union[int, str, Batches]
CompoundLike = Union[int, str, Compounds]
NullableCompoundLike = Union[None, int, str, Compounds]
SensorLike = Union[int, str, Sensors]
SensorDataLike = Union[None, Sequence[float], bytes, str]
StimulusLike = Union[Stimuli, int, str]
CompoundsLike = Union[CompoundLike, Iterable[CompoundLike]]
BatchesLike = Union[BatchLike, Iterable[BatchLike]]
NullableCompoundsLike = Union[None, Compounds, int, str, Iterable[Union[None, Compounds, int, str]]]
