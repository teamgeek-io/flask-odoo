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
        if hasattr(ctx, "odoo_common"):
            delattr(ctx, "odoo_common")
        if hasattr(ctx, "odoo_uid"):
            delattr(ctx, "odoo_uid")

    def create_common(self):
        ODOO_URL = current_app.config["ODOO_URL"]
        common = xmlrpc.client.ServerProxy(
            "{}/xmlrpc/2/common".format(ODOO_URL)
        )
        return common

    @property
    def common(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "odoo_common"):
                ctx.odoo_common = self.create_common()
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
            return ctx.odoo_common
