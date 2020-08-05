import logging
import xmlrpc.client

from flask import _app_ctx_stack, current_app

__version__ = "0.0.1"

logger = logging.getLogger(__name__)


class Odoo:
    """Stores Odoo XML RPC server proxies and authentication information
    inside Flask's application context.

    """

    def __init__(self, app=None):
        self.app = app
        if self.app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        for name in ["odoo_common", "odoo_object"]:
            server_proxy = getattr(ctx, name, None)
            if server_proxy:
                server_proxy.close()
                delattr(ctx, name)
        if hasattr(ctx, "odoo_uid"):
            delattr(ctx, "odoo_uid")

    def create_common_proxy(self):
        ODOO_URL = current_app.config["ODOO_URL"]
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
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
        ODOO_DB = current_app.config["ODOO_DB"]
        ODOO_USERNAME = current_app.config["ODOO_USERNAME"]
        ODOO_PASSWORD = current_app.config["ODOO_PASSWORD"]
        uid = self.common.authenticate(
            ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}
        )
        return uid

    @property
    def uid(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_uid"):
                ctx.odoo_uid = self.authenticate()
            return ctx.odoo_uid

    def create_object_proxy(self):
        ODOO_URL = current_app.config["ODOO_URL"]
        object = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        return object

    @property
    def object(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_object"):
                ctx.odoo_object = self.create_object_proxy()
            return ctx.odoo_object

    def __getitem__(self, key):
        ODOO_DB = current_app.config["ODOO_DB"]
        ODOO_PASSWORD = current_app.config["ODOO_PASSWORD"]
        return Model(key, self.object, ODOO_DB, self.uid, ODOO_PASSWORD)


class Model:
    """Simplifies working with Odoo models through XML RPC.

    Args:
        name: Odoo model name.
        proxy: XML RPC server proxy.
        db: The database to use.
        uid: The user id (retrieved through `authenticate`).
        password: The user’s password.

    Examples:
        >>> odoo["res.partner"].execute_kw("check_access_rights", "read",
        ...                                raise_exception=False)
        true

    """

    def __init__(
        self,
        name: str,
        proxy: xmlrpc.client.ServerProxy,
        db: str,
        uid: int,
        password: str,
    ):
        self.name = name
        self.proxy = proxy
        self.db = db
        self.uid = uid
        self.password = password

    def execute_kw(self, method_name, *args, **kwargs):
        """Call `method_name` on this model and return the result."""
        return self.proxy.execute_kw(
            self.db,
            self.uid,
            self.password,
            self.name,
            method_name,
            args,
            kwargs,
        )

    def __getattr__(self, name):
        return Method(name, self)

    def __repr__(self):
        return (
            f"<Model(name='{self.name}', proxy={self.proxy}, db='{self.db}')>"
        )


class Method:
    """Simplifies calling methods on Odoo models through XML RPC.

    Args:
        name: The method name.
        model: The Odoo model.

    Examples:
        >>> odoo["res.partner"].check_access_rights("read",
        ...                                         raise_exception=False)
        true

    """

    def __init__(self, name, model):
        self.name = name
        self.model = model

    def __call__(self, *args, **kwargs):
        return self.model.execute_kw(self.name, *args, **kwargs)

    def __repr__(self):
        return f"<Method(name='{self.name}', model={self.model})>"
