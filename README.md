
# Flask-Odoo

Flask-Odoo is an extension for [Flask](https://flask.palletsprojects.com/) that aims to simplify the integration with the [Odoo](https://www.odoo.com/) XML-RPC [External API](https://www.odoo.com/documentation/13.0/webservices/odoo.html).

## Installing

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```
$ pip install -U Flask-Odoo
```

# Example

Initialize the Flask extension:

```
from flask import Flask
from flask_odoo import Odoo

app = Flask(__name__)
app.config["ODOO_URL"] = "http://localhost:8069"
app.config["ODOO_DB"] = "odoo"
app.config["ODOO_USERNAME"] = "admin"
app.config["ODOO_PASSWORD"] = "admin"
odoo = Odoo(app)
```

then fetch the Odoo version information by:

```
>>> odoo.common.version()
{
    "server_version": "13.0",
    "server_version_info": [13, 0, 0, "final", 0],
    "server_serie": "13.0",
    "protocol_version": 1,
}
```

or call a method on an Odoo model:

```
>>> odoo["res.partner"].check_access_rights("read", raise_exception=False)
true
```

# Contributing

Setup your development environment by running:

```
$ make
```

this will create a new Python *virtualenv*, install all necessary dependencies and run the tests.
