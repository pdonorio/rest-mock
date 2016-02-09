
# rest-mock

A python3 flask HTTP server mapping classes into REST API endpoints;
**the base** for any middleware APIs in my projects.

It comes bundled with:

* RESTful classes to write endpoints
* decorators to add properties and parameters
* as many best practices i found in my experience for Flask
* easy configuration
* sqlalchemy (sqllite as default) backend
* any database/resource pluggable (in fact, you can write your own)
* security handling (JWT token will be added)
* administration

---

## Documentation

**WARNING:
the documentation is outdated, i will try to fix it anytime soon**

You can find a compiled version on [readthedocs website](http://rest-mock.readthedocs.org/en/latest/).

Here is the index for browsing it internally on GitHub:

* [Introduction](docs/index.md)
* [Quick start](docs/quick.md)
* [Configuration](docs/conf.md)
* [Run the server](docs/run.md)
* [Manage APIs](docs/manage.md)
* [Security](docs/security.md)

---

## Creator(s)

* [Paolo D'Onorio De Meo](https://twitter.com/paolodonorio/)

## Copyright and license

Code and documentation copyright: `Paolo D'Onorio De Meo @2015`.

Code released under the [MIT license](LICENSE).
