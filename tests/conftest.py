import pytest
from flask import Flask


@pytest.fixture
def app():
    import_name = __name__.split(".")[0]
    app = Flask(import_name)
    app.config["ODOO_URL"] = "http://localhost:8069"
    app.config["ODOO_DB"] = "odoo"
    app.config["ODOO_USERNAME"] = "admin"
    app.config["ODOO_PASSWORD"] = "admin"
    yield app


@pytest.fixture
def app_context(app):
    with app.app_context() as app_context:
        yield app_context


@pytest.fixture
def request_context(app):
    with app.test_request_context() as request_context:
        yield request_context
