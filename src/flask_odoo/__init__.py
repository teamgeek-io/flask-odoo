import logging
import xmlrpc.client

import schematics
from flask import _app_ctx_stack, current_app

__version__ = "0.1.0"

logger = logging.getLogger(__name__)


class Odoo:
    """Stores Odoo XML-RPC server proxies and authentication information
    inside Flask's application context.

    """

    def __init__(self, app=None):
        self.app = app
        self.Model = self.make_model_base()

        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("ODOO_URL", "")
        app.config.setdefault("ODOO_DB", "")
        app.config.setdefault("ODOO_USERNAME", "")
        app.config.setdefault("ODOO_PASSWORD", "")

        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        for name in ["odoo_common", "odoo_object"]:
            server_proxy = getattr(ctx, name, None)
            if server_proxy:
                server_proxy._ServerProxy__close()
                delattr(ctx, name)
        if hasattr(ctx, "odoo_uid"):
            delattr(ctx, "odoo_uid")

    def create_common_proxy(self):
        url = current_app.config["ODOO_URL"]
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        return common

    @property
    def common(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_common"):
                ctx.odoo_common = self.create_common_proxy()
            return ctx.odoo_common

    def authenticate(self):
        """Returns a user identifier (uid) used in authenticated calls."""
        db = current_app.config["ODOO_DB"]
        username = current_app.config["ODOO_USERNAME"]
        password = current_app.config["ODOO_PASSWORD"]
        uid = self.common.authenticate(db, username, password, {})
        return uid

    @property
    def uid(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_uid"):
                ctx.odoo_uid = self.authenticate()
            return ctx.odoo_uid

    def create_object_proxy(self):
        url = current_app.config["ODOO_URL"]
        object = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        return object

    @property
    def object(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_object"):
                ctx.odoo_object = self.create_object_proxy()
            return ctx.odoo_object

    def __getitem__(self, key):
        return ObjectProxy(self, key)

    def make_model_base(self):
        """Return a base that all models will inherit from."""

        # TODO: In future, consider defining BaseModel outside this function
        class BaseModel(schematics.models.Model):
            odoo = self
            _name = None

            id = schematics.types.IntType()

            @classmethod
            def _model_name(cls):
                return cls._name or cls.__name__.lower()

            @classmethod
            def search_count(cls, domain=[]):
                model_name = cls._model_name()
                return cls.odoo[model_name].search_count(domain)

            @classmethod
            def search_read(cls, domain=[], offset=None, limit=None):
                model_name = cls._model_name()
                fields = [
                    field.serialized_name or name
                    for name, field in cls._schema.fields.items()
                ]
                kwargs = {"fields": fields}
                if offset:
                    kwargs["offset"] = offset
                if limit:
                    kwargs["limit"] = limit
                records = cls.odoo[model_name].search_read(domain, **kwargs)
                return [cls(rec) for rec in records]

            @classmethod
            def search_by_id(cls, id):
                domain = [["id", "=", id]]
                objects = cls.search_read(domain, limit=1)
                return objects[0] if objects else None

            def create_or_update(self):
                model_name = self._model_name()
                vals = self.to_primitive()
                vals.pop("id", None)
                if self.id:
                    self.odoo[model_name].write([self.id, vals])
                else:
                    self.id = self.odoo[model_name].create(vals)

            def delete(self):
                model_name = self._model_name()
                if self.id:
                    self.odoo[model_name].unlink([self.id])

            def __repr__(self):
                return f"<{self.__class__.__name__}(id={self.id})>"

        return BaseModel


class ObjectProxy:
    """Simplifies calling methods of Odoo models via the `execute_kw` RPC function.

    Args:
        odoo: Instance of the `Odoo` class.
        model_name: Odoo model name.

    Examples:
        >>> odoo["res.partner"].check_access_rights("read",
        ...                                         raise_exception=False)
        true

    """

    class Method:
        def __init__(self, odoo: Odoo, model_name: str, name: str):
            self.odoo = odoo
            self.model_name = model_name
            self.name = name

        def __call__(self, *args, **kwargs):
            db = current_app.config["ODOO_DB"]
            password = current_app.config["ODOO_PASSWORD"]
            return self.odoo.object.execute_kw(
                db,
                self.odoo.uid,
                password,
                self.model_name,
                self.name,
                args,
                kwargs,
            )

        def __repr__(self):
            return (
                "<ObjectProxy.Method("
                f"model_name={self.model_name}, "
                f"name='{self.name}'"
                ")>"
            )

    def __init__(self, odoo: Odoo, model_name: str):
        self.odoo = odoo
        self.model_name = model_name

    def __getattr__(self, name):
        return self.Method(self.odoo, self.model_name, name)

    def __repr__(self):
        return f"<ObjectProxy(model_name='{self.model_name}')>"
