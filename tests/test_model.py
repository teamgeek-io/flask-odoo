from unittest.mock import MagicMock

import schematics.models

from flask_odoo import Odoo
from flask_odoo.model import make_model_base
from schematics.types.serializable import serializable


def test_make_model_base():
    odoo_mock = MagicMock()
    Model = make_model_base(odoo_mock)
    assert issubclass(Model, schematics.models.Model)
    assert Model._odoo is odoo_mock


def test_base_model_no_name(app, app_context):
    odoo_mock = MagicMock()
    Model = make_model_base(odoo_mock)

    class Partner(Model):
        pass

    assert Partner._model_name() == "partner"


def test_base_model_with_name(app, app_context):
    odoo_mock = MagicMock()
    Model = make_model_base(odoo_mock)

    class Partner(Model):
        _name = "res.partner"

    assert Partner._model_name() == "res.partner"


def test_base_model_no_domain(app, app_context):
    odoo_mock = MagicMock()
    Model = make_model_base(odoo_mock)

    class Partner(Model):
        _name = "res.partner"

    expected_domain = [["is_company", "=", True]]
    search_criteria = [["is_company", "=", True]]
    domain = Partner._construct_domain(search_criteria)
    assert domain == expected_domain


def test_base_model_with_domain(app, app_context):
    odoo_mock = MagicMock()
    Model = make_model_base(odoo_mock)

    class Partner(Model):
        _name = "res.partner"
        _domain = [["active", "=", True]]

    expected_domain = [["active", "=", True], ["is_company", "=", True]]
    search_criteria = [["is_company", "=", True]]
    domain = Partner._construct_domain(search_criteria)
    assert domain == expected_domain


def test_base_model_search_count(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()
    app_context.odoo_object.execute_kw.return_value = 2

    class Partner(odoo.Model):
        _name = "res.partner"

    search_criteria = [["is_company", "=", True]]
    count = Partner.search_count(search_criteria)

    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "search_count",
        (search_criteria,),
        {},
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

        name = odoo.StringType()
        is_active = odoo.BooleanType(serialized_name="active")

    search_criteria = [["is_company", "=", True]]
    objects = Partner.search_read(
        search_criteria, offset=100, limit=10, order="id"
    )
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "search_read",
        (search_criteria,),
        {
            "fields": ["id", "name", "active"],
            "offset": 100,
            "limit": 10,
            "order": "id",
        },
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

        name = odoo.StringType()

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

        name = odoo.StringType()

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
        ([2], {"name": "new_name"}),
        {},
    )


def test_base_model_create_or_update_no_serializable(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()

    class Partner(odoo.Model):
        _name = "res.partner"

        name = odoo.StringType()

        @serializable
        def serializable_field(self):
            return ""

    partner = Partner()
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


def test_base_model_create_or_update_no_one2many(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()

    class Partner(odoo.Model):
        _name = "res.partner"

        name = odoo.StringType()
        related_model_ids = odoo.One2manyType()

    partner = Partner()
    partner.name = "test_partner"
    partner.related_model_ids = [1, 2, 3]
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


def test_base_model_create_or_update_many2one(app, app_context):
    odoo = Odoo(app)
    app_context.odoo_common = MagicMock()
    app_context.odoo_common.authenticate.return_value = 1
    app_context.odoo_object = MagicMock()

    class Partner(odoo.Model):
        _name = "res.partner"

        name = odoo.StringType()
        related_model_id = odoo.Many2oneType()

    partner = Partner()
    partner.name = "test_partner"
    partner.related_model_id = [2, "related"]
    partner.create_or_update()
    app_context.odoo_object.execute_kw.assert_called_with(
        "odoo",
        1,
        "admin",
        "res.partner",
        "create",
        ({"name": "test_partner", "related_model_id": 2},),
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


def test_base_model_repr(app):
    odoo = Odoo(app)

    class Partner(odoo.Model):
        _name = "res.partner"

    partner = Partner()
    partner.id = 1
    assert str(partner) == "<Partner(id=1)>"
