from unittest.mock import MagicMock

from flask_odoo import Odoo, Model, Method


def test_odoo_init(app, mocker):
    mocked_init_app = mocker.patch.object(Odoo, "init_app")
    odoo = Odoo(app)
    assert odoo.app == app
    mocked_init_app.assert_called_with(app)


def test_odoo_common(app, app_context, mocker):
    mocked_server_proxy = mocker.patch("flask_odoo.xmlrpc.client.ServerProxy")
    odoo = Odoo(app)
    common_proxy = odoo.common
    assert app_context.odoo_common == common_proxy
    mocked_server_proxy.assert_called_with(
        "http://localhost:8069/xmlrpc/2/common"
    )


def test_odoo_authenticate(app, app_context, mocker):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    mocked_authenticate = mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=1
    )
    uid = odoo.authenticate()
    mocked_authenticate.assert_called_with("odoo", "admin", "admin", {})
    assert uid == 1


def test_odoo_uid(app, app_context, mocker):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=2
    )
    assert odoo.uid == 2


def test_odoo_object(app, app_context, mocker):
    mocked_server_proxy = mocker.patch("flask_odoo.xmlrpc.client.ServerProxy")
    odoo = Odoo(app)
    object_proxy = odoo.object
    assert app_context.odoo_object == object_proxy
    mocked_server_proxy.assert_called_with(
        "http://localhost:8069/xmlrpc/2/object"
    )


def test_odoo_getitem(app, app_context, mocker):
    app_context.odoo_common = MagicMock()
    mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=3
    )
    app_context.odoo_object = MagicMock()
    odoo = Odoo(app)
    model = odoo["test.model"]
    assert isinstance(model, Model)
    assert model.name == "test.model"
    assert model.proxy == app_context.odoo_object
    assert model.db == "odoo"
    assert model.uid == 3
    assert model.password == "admin"


def test_model_init():
    mocked_proxy = MagicMock()
    model = Model("test.model", mocked_proxy, "test_db", 4, "test_password")
    assert model.name == "test.model"
    assert model.proxy == mocked_proxy
    assert model.db == "test_db"
    assert model.uid == 4
    assert model.password == "test_password"


def test_model_execute_kw():
    mocked_proxy = MagicMock()
    model = Model("test.model", mocked_proxy, "test_db", 4, "test_password")
    model.execute_kw("test_method", "arg1", kwarg1="test_kwarg")
    mocked_proxy.execute_kw.assert_called_with(
        "test_db",
        4,
        "test_password",
        "test.model",
        "test_method",
        ("arg1",),
        {"kwarg1": "test_kwarg"},
    )


def test_model_getattr():
    mocked_proxy = MagicMock()
    model = Model("test.model", mocked_proxy, "test_db", 5, "test_password")
    method = model.test_method
    assert isinstance(method, Method)
    assert method.name == "test_method"
    method("arg1", kwarg1="test_kwarg")
    mocked_proxy.execute_kw.assert_called_with(
        "test_db",
        5,
        "test_password",
        "test.model",
        "test_method",
        ("arg1",),
        {"kwarg1": "test_kwarg"},
    )
