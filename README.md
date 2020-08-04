
# Flask-Odoo

Flask-Odoo is an extension for [Flask](https://flask.palletsprojects.com/) that aims to simplify the integration with the [Odoo](https://www.odoo.com/) XML-RPC [External API](https://www.odoo.com/documentation/13.0/webservices/odoo.html).

## Installing

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```
$ pip install -U Flask-Odoo
```

# Example

```
from flask import Flask
from flask_odoo import Odoo

app = Flask(__name__)
app.config["ODOO_URL"] = "http://localhost:8069"
app.config["ODOO_DB"] = "odoo"
app.config["ODOO_USERNAME"] = "admin"
app.config["ODOO_PASSWORD"] = "admin"
odoo = Odoo(app)

version = odoo.common.version()
```

# Contributing

Setup your development environment by running:

```
$ make
```

this will create a new Python *virtualenv*, install all necessary dependencies and run the tests.
