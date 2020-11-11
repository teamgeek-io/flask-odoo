import schematics

from .types import Many2oneType


def _model_name(cls):
    return cls._name or cls.__name__.lower()


def _construct_domain(cls, search_criteria: list = None):
    domain = []
    if cls._domain:
        domain.extend(cls._domain)
    if search_criteria:
        domain.extend(search_criteria)
    return domain


def search_count(cls, search_criteria: list = None):
    model_name = cls._model_name()
    domain = cls._construct_domain(search_criteria)
    return cls._odoo[model_name].search_count(domain)


def fields_get(cls):
    model_name = cls._model_name()
    return cls._odoo[model_name].fields_get()


def search_read(
    cls,
    search_criteria: list = None,
    offset: int = None,
    limit: int = None,
    order: str = None,
):
    model_name = cls._model_name()
    domain = cls._construct_domain(search_criteria)
    fields = [
        field.serialized_name or name
        for name, field in cls._schema.fields.items()
        if not isinstance(field, schematics.types.Serializable)
    ]
    kwargs = {"fields": fields}
    if offset:
        kwargs["offset"] = offset
    if limit:
        kwargs["limit"] = limit
    if order:
        kwargs["order"] = order
    records = cls._odoo[model_name].search_read(domain, **kwargs)
    return [cls(rec) for rec in records]


def search_by_id(cls, id):
    search_criteria = [["id", "=", id]]
    objects = cls.search_read(search_criteria, limit=1)
    return objects[0] if objects else None


def create_or_update(self):
    model_name = self._model_name()
    vals = self.to_primitive()
    vals.pop("id", None)
    for name, field in self._schema.fields.items():
        key = field.serialized_name or name
        if isinstance(field, schematics.types.Serializable):
            vals.pop(key, None)
        elif isinstance(field, Many2oneType):
            if key in vals:
                vals[key] = vals[key][0]
        else:
            pass
    if self.id:
        self._odoo[model_name].write([self.id], vals)
    else:
        self.id = self._odoo[model_name].create(vals)


def delete(self):
    model_name = self._model_name()
    if self.id:
        self._odoo[model_name].unlink([self.id])


def __repr__(self):
    return f"<{self.__class__.__name__}(id={self.id})>"


def make_model_base(odoo):
    """Return a base class for Odoo models to inherit from."""
    return type(
        "BaseModel",
        (schematics.models.Model,),
        dict(
            _odoo=odoo,
            _name=None,
            _domain=None,
            id=schematics.types.IntType(),
            _model_name=classmethod(_model_name),
            _construct_domain=classmethod(_construct_domain),
            search_count=classmethod(search_count),
            search_read=classmethod(search_read),
            search_by_id=classmethod(search_by_id),
            fields_get=classmethod(fields_get),
            create_or_update=create_or_update,
            delete=delete,
            __repr__=__repr__,
        ),
    )
