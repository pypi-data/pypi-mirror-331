# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses

from .arg import REQ, rm_na
from .exc import ParamError


class MetadataKeyEnum(str, enum.Enum):
    CONVERTER = "_better_dataclass_converter"


T_DATA = T.Dict[str, T.Any]
T_FIELDS = T.Dict[str, dataclasses.Field]

_class_fields: T.Dict[T.Any, T_FIELDS] = {}  # class fields cache
T_DATA_LIKE = T.Union[T_DATA, "T_BASE"]


@dataclasses.dataclass
class Base:
    @classmethod
    def get_fields(cls) -> T_FIELDS:
        """
        Get the dict view of the ``dataclasses.Field`` in this class.
        It leverages the cache to avoid the overhead of ``dataclasses.fields``
        function call.
        """
        try:
            return _class_fields[cls]
        except KeyError:
            _class_fields[cls] = {
                field.name: field for field in dataclasses.fields(cls)
            }
            return _class_fields[cls]

    def to_dict(
        self,
    ) -> T.Dict[str, T.Any]:
        dct = dataclasses.asdict(self)
        return rm_na(**dct)

    def _validate(self):
        for field in dataclasses.fields(self.__class__):
            if field.init:
                k = field.name
                if isinstance(getattr(self, k), REQ):  # pragma: no cover
                    raise ParamError(f"Field {k!r} is required for {self.__class__}.")

    def __post_init__(self):
        self._validate()

    @classmethod
    def from_dict(
        cls,
        dct: T_DATA,
    ):
        """
        Construct an instance from dataclass-like data.
        """
        _fields = cls.get_fields()
        kwargs = {}
        for field_name, field in _fields.items():
            try:
                kwargs[field_name] = dct[field_name]
            except KeyError:
                pass
        return cls(**kwargs)


T_BASE = T.TypeVar("T_BASE", bound=Base)
