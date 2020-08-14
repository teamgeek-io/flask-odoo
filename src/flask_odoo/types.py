import schematics.types

from schematics.exceptions import ConversionError
from schematics.translator import _
from schematics.types import BooleanType

__all__ = [
    "BooleanType",
    "StringType",
    "IntType",
    "FloatType",
    "DecimalType",
    "DateType",
    "DateTimeType",
    "UTCDateTimeType",
    "TimestampType",
    "ListType",
    "DictType",
    "One2manyType",
    "Many2oneType",
]


class OdooTypeMixin:
    def to_native(self, value, context=None):
        if (
            not issubclass(self.__class__, schematics.types.BooleanType)
            and value is False
        ):
            return None
        return super().to_native(value, context)


class StringType(OdooTypeMixin, schematics.types.StringType):
    pass


class IntType(OdooTypeMixin, schematics.types.IntType):
    pass


class FloatType(OdooTypeMixin, schematics.types.FloatType):
    pass


class DecimalType(OdooTypeMixin, schematics.types.DecimalType):
    pass


class DateType(OdooTypeMixin, schematics.types.DateType):
    pass


class DateTimeType(OdooTypeMixin, schematics.types.DateTimeType):
    pass


class UTCDateTimeType(OdooTypeMixin, schematics.types.UTCDateTimeType):
    pass


class TimestampType(OdooTypeMixin, schematics.types.TimestampType):
    pass


class ListType(OdooTypeMixin, schematics.types.ListType):
    pass


class DictType(OdooTypeMixin, schematics.types.DictType):
    pass


class One2manyType(OdooTypeMixin, schematics.types.ListType):
    """A field that stores an Odoo One2many value."""

    def __init__(self, *args, **kwargs):
        super().__init__(schematics.types.IntType, *args, **kwargs)


class Many2oneType(schematics.types.BaseType):
    """A field that stores an Odoo Many2one value."""

    primitive_type = list
    native_type = list
    length = 2

    MESSAGES = {
        "convert": _("Couldn't interpret '{0}' as Many2one value."),
        "length": _("Many2one value must contain exactly {0} items."),
    }

    def to_native(self, value, context=None):
        if value is False:
            return None
        if isinstance(value, int):
            return [value, ""]
        if isinstance(value, str):
            try:
                return [int(value), ""]
            except ValueError:
                raise ConversionError(self.messages["convert"].format(value))
        if isinstance(value, list) or isinstance(value, tuple):
            if len(value) != self.length:
                raise ConversionError(
                    self.messages["length"].format(self.length)
                )
            try:
                return [int(value[0]), str(value[1])]
            except ValueError:
                raise ConversionError(self.messages["convert"].format(value))
            return value
        raise ConversionError(self.messages["convert"].format(value))

    def to_primitive(self, value, context=None):
        return value
