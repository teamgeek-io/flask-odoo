from flask import Flask

from flask_odoo import Odoo


def test_init(mocker):
    mocked_init_app = mocker.patch.object(Odoo, "init_app")

    import_name = __name__.split(".")[0]
    app = Flask(import_name)
    app.config["ODOO_URL"] = "http://localhost:8069"
    app.config["ODOO_DB"] = "odoo"
    app.config["ODOO_USERNAME"] = "admin"
    app.config["ODOO_PASSWORD"] = "admin"

    odoo = Odoo(app)

    assert odoo.app == app
    with app.app_context() as app_context:
        common = odoo.common
        assert app_context.odoo_common == common
    mocked_init_app.assert_called_with(app)
