import schematics
import pytest

from flask_odoo.types import (
    OdooTypeMixin,
    StringType,
    IntType,
    FloatType,
    DecimalType,
    DateType,
    DateTimeType,
    UTCDateTimeType,
    TimestampType,
    ListType,
    DictType,
    One2manyType,
    Many2oneType,
)


def test_odoo_type_mixin():
    class BaseType:
        def to_native(self, value):
            return ""

    class TestType(OdooTypeMixin, BaseType):
        pass

    base_type = BaseType()
    assert base_type.to_native(False) == ""
    test_type = TestType()
    assert test_type.to_native(False) is None


def test_string_type():
    assert issubclass(StringType, (OdooTypeMixin, schematics.types.StringType))


def test_int_type():
    assert issubclass(IntType, (OdooTypeMixin, schematics.types.IntType))


def test_float_type():
    assert issubclass(FloatType, (OdooTypeMixin, schematics.types.FloatType))


def test_decimal_type():
    assert issubclass(
        DecimalType, (OdooTypeMixin, schematics.types.DecimalType)
    )


def test_date_type():
    assert issubclass(DateType, (OdooTypeMixin, schematics.types.DateType))


def test_date_time_type():
    assert issubclass(
        DateTimeType, (OdooTypeMixin, schematics.types.DateTimeType)
    )


def test_utc_date_time_type():
    assert issubclass(
        UTCDateTimeType, (OdooTypeMixin, schematics.types.UTCDateTimeType)
    )


def test_timestamp_type():
    assert issubclass(
        TimestampType, (OdooTypeMixin, schematics.types.TimestampType)
    )


def test_list_type():
    assert issubclass(ListType, (OdooTypeMixin, schematics.types.ListType))


def test_dict_type():
    assert issubclass(DictType, (OdooTypeMixin, schematics.types.DictType))


def test_one2many_type():
    assert issubclass(One2manyType, (OdooTypeMixin, schematics.types.ListType))
    instance = One2manyType()
    assert isinstance(instance.field, schematics.types.IntType)


def test_many2one_type():
    assert issubclass(Many2oneType, (OdooTypeMixin, schematics.types.BaseType))
    assert Many2oneType.primitive_type is list
    assert Many2oneType.native_type is list
    assert Many2oneType.length == 2
    instance = Many2oneType()
    assert instance.to_native(False) is None
    with pytest.raises(schematics.exceptions.ConversionError):
        instance.to_native("")
    with pytest.raises(schematics.exceptions.ConversionError):
        instance.to_native(["Test", 1])
    assert instance.to_native([1, "Test"]) == [1, "Test"]
    assert instance.to_native(["1", "Test"]) == [1, "Test"]
