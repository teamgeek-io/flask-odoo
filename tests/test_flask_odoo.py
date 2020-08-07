from unittest.mock import MagicMock

from flask_odoo import Odoo, ObjectProxy


def test_odoo_init(app, mocker):
    init_app_mock = mocker.patch.object(Odoo, "init_app")
    odoo = Odoo(app)
    assert odoo.app == app
    init_app_mock.assert_called_with(app)


def test_odoo_common(app, app_context, mocker):
    server_proxy_mock = mocker.patch("flask_odoo.xmlrpc.client.ServerProxy")
    odoo = Odoo(app)
    server_proxy = odoo.common
    assert app_context.odoo_common == server_proxy
    server_proxy_mock.assert_called_with(
        "http://localhost:8069/xmlrpc/2/common"
    )


def test_odoo_authenticate(app, app_context, mocker):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    authenticate_mock = mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=1
    )
    uid = odoo.authenticate()
    authenticate_mock.assert_called_with("odoo", "admin", "admin", {})
    assert uid == 1


def test_odoo_uid(app, app_context, mocker):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=1
    )
    assert odoo.uid == 1


def test_odoo_object(app, app_context, mocker):
    server_proxy_mock = mocker.patch("flask_odoo.xmlrpc.client.ServerProxy")
    odoo = Odoo(app)
    server_proxy = odoo.object
    assert app_context.odoo_object == server_proxy
    server_proxy_mock.assert_called_with(
        "http://localhost:8069/xmlrpc/2/object"
    )


def test_odoo_getitem(app, app_context, mocker):
    app_context.odoo_common = MagicMock()
    mocker.patch.object(
        app_context.odoo_common, "authenticate", return_value=1
    )
    app_context.odoo_object = MagicMock()
    odoo = Odoo(app)
    object_proxy = odoo["test.model"]
    assert isinstance(object_proxy, ObjectProxy)
    object_proxy.odoo == odoo
    assert object_proxy.model_name == "test.model"


def test_object_proxy_init():
    odoo_mock = MagicMock()
    object_proxy = ObjectProxy(odoo_mock, "test.model")
    assert object_proxy.odoo == odoo_mock
    assert object_proxy.model_name == "test.model"


def test_object_proxy_getattr():
    odoo_mock = MagicMock()
    object_proxy = ObjectProxy(odoo_mock, "test.model")
    method = object_proxy.test_method
    assert isinstance(method, ObjectProxy.Method)
    assert method.odoo == odoo_mock
    assert method.model_name == "test.model"
    assert method.name == "test_method"


def test_object_proxy_method_init():
    odoo_mock = MagicMock()
    method = ObjectProxy.Method(odoo_mock, "test.model", "test_method")
    assert method.odoo == odoo_mock
    assert method.model_name == "test.model"
    assert method.name == "test_method"


def test_object_proxy_method_call(app, app_context, mocker):
    odoo_mock = MagicMock()
    odoo_mock.uid = 1
    odoo_mock.object = MagicMock()
    method = ObjectProxy.Method(odoo_mock, "test.model", "test_method")
    method("arg1", kwarg1="test_kwarg")
    odoo_mock.object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "test.model",
        "test_method",
        ("arg1",),
        {"kwarg1": "test_kwarg"},
    )
