# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import pytest

from atlas_doc_parser.base import Base, T_DATA
from atlas_doc_parser.arg import REQ, NA
from atlas_doc_parser.exc import ParamError
from atlas_doc_parser.tests import check_seder


verbose = False


@dataclasses.dataclass
class Model(Base):
    attr1: int = dataclasses.field(default_factory=REQ)
    attr2: int = dataclasses.field(default_factory=NA)

    def special_method(self):
        if verbose:
            print("call special_method")


@dataclasses.dataclass
class Profile(Base):
    """
    firstname, lastname, ssn are generic data type field.
    """

    firstname: str = dataclasses.field(default_factory=REQ)
    lastname: str = dataclasses.field(default_factory=REQ)
    ssn: str = dataclasses.field(default_factory=REQ)

    def special_profile_method(self):
        if verbose:
            print("call special_profile_method")


@dataclasses.dataclass
class Degree(Base):
    name: str = dataclasses.field(default_factory=REQ)
    year: int = dataclasses.field(default_factory=REQ)

    def special_degree_method(self):
        if verbose:
            print("call special_degree_method")


@dataclasses.dataclass
class People(Base):
    """
    - ``profile`` is nested field.
    - ``degrees`` is collection type field.
    """

    # fmt: off
    id: int = dataclasses.field(default_factory=REQ)
    profile: Profile = dataclasses.field(default_factory=NA)
    degrees: T.List[Degree] = dataclasses.field(default_factory=NA)
    # fmt: on

    @classmethod
    def from_dict(
        cls,
        dct: T_DATA,
    ) -> "Base":
        if "profile" in dct:
            dct["profile"] = Profile.from_dict(dct["profile"])
        if "degrees" in dct:
            dct["degrees"] = [Degree.from_dict(d) for d in dct["degrees"]]
        return super().from_dict(dct)

    def special_people_method(self):
        if verbose:
            print("call special_people_method")


class TestBase:
    def test_req_and_na(self):
        model = Model(attr1=1)
        check_seder(model)

        model = Model(attr1=1, attr2=2)
        check_seder(model)

        with pytest.raises(ParamError):
            model = Model()

        model = Model.from_dict(dict(attr1=1))
        check_seder(model)
        model.special_method()  # type hint works

        model = Model.from_dict(dict(attr1=1, attr2=2))
        check_seder(model)
        model.special_method()  # type hint works

        with pytest.raises(ParamError):
            model = Model.from_dict(dict())

        model = Model.from_dict(dict(attr1=1, attr2=2, attr3=3))
        model.special_method()  # type hint works

    def test_profile_degrees_default_value(self):
        people = People(id=1)
        check_seder(people)

        assert isinstance(people.profile, NA)
        assert isinstance(people.degrees, NA)

        people = People(
            id=1,
            profile=Profile(firstname="David", lastname="John", ssn="123-45-6789"),
            degrees=[
                Degree(name="Bachelor", year=2004),
                Degree(name="Master", year=2006),
            ],
        )
        check_seder(people)


if __name__ == "__main__":
    from atlas_doc_parser.tests import run_cov_test

    run_cov_test(__file__, "atlas_doc_parser.base", preview=False)
