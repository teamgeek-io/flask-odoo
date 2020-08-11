from unittest.mock import MagicMock

import schematics.models
import schematics.types

from flask_odoo import ObjectProxy, Odoo


def test_odoo_init(app, mocker):
    init_app_mock = mocker.patch.object(Odoo, "init_app")
    odoo = Odoo(app)
    assert odoo.app == app
    assert isinstance(odoo.Model, type)
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


def test_odoo_getitem(app, app_context):
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    odoo = Odoo(app)
    object_proxy = odoo["test.model"]
    assert isinstance(object_proxy, ObjectProxy)
    object_proxy.odoo == odoo
    assert object_proxy.model_name == "test.model"


def test_odoo_make_model_base(app, app_context):
    odoo = Odoo(app)
    Model = odoo.make_model_base()

    class Partner(Model):
        _name = "res.partner"

    partner = Partner()

    assert isinstance(partner, schematics.models.Model)
    assert partner.odoo is odoo
    assert partner._name == "res.partner"


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


def test_object_proxy_method_call(app, app_context):
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


def test_base_model_no_name(app, app_context):
    odoo = Odoo(app)
    Model = odoo.make_model_base()

    class Partner(Model):
        pass

    partner = Partner()
    assert partner._model_name() == "partner"


def test_base_model_search_count(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    app_context.odoo_object.execute_kw.return_value = 2

    class Partner(odoo.Model):
        _name = "res.partner"

    domain = [["is_company", "=", True]]
    count = Partner.search_count(domain)

    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo", 1, "admin", "res.partner", "search_count", (domain,), {}
    )
    assert count == 2


def test_base_model_search_read(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    records = [
        {"id": 1, "name": "rec1", "active": True},
        {"id": 2, "name": "rec2", "active": False},
    ]
    app_context.odoo_object.execute_kw.return_value = records

    class Partner(odoo.Model):
        _name = "res.partner"
        name = schematics.types.StringType()
        is_active = schematics.types.BooleanType(serialized_name="active")

    domain = [["is_company", "=", True]]
    objects = Partner.search_read(domain, offset=100, limit=10)
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "search_read",
        (domain,),
        {"fields": ["id", "name", "active"], "offset": 100, "limit": 10},
    )
    assert objects == [Partner(records[0]), Partner(records[1])]
    assert objects[0].is_active
    assert not objects[1].is_active


def test_base_model_search_by_id(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    app_context.odoo_object.execute_kw.return_value = [
        {"id": 2, "name": "test_partner"}
    ]

    class Partner(odoo.Model):
        _name = "res.partner"
        name = schematics.types.StringType()

    partner = Partner.search_by_id(2)
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "search_read",
        ([["id", "=", 2]],),
        {"fields": ["id", "name"], "limit": 1},
    )
    assert partner.id == 2
    assert partner.name == "test_partner"


def test_base_model_create_or_update(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    app_context.odoo_object.execute_kw.return_value = 2

    class Partner(odoo.Model):
        _name = "res.partner"
        name = schematics.types.StringType()

    partner = Partner()
    assert not partner.id
    partner.name = "test_partner"
    partner.create_or_update()
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "create",
        ({"name": "test_partner"},),
        {},
    )
    assert partner.id == 2
    partner.name = "new_name"
    partner.create_or_update()
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "write",
        ([2, {"name": "new_name"}],),
        {},
    )


def test_base_model_delete(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()

    class Partner(odoo.Model):
        _name = "res.partner"

    partner = Partner()
    partner.id = 2
    partner.delete()
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo", 1, "admin", "res.partner", "unlink", ([2],), {}
    )
