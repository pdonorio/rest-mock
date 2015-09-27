# rest-mock

`A python3 flask server mapping classes into mock REST API end-points.`

The future **base** for any middleware APIs project of mine :)


---

## Project motivations

I have been working off Flask for a quite time now; and since Python is a language about being better (also a [better you](http://pile.wf/about-being-better/)) i am trying to rewrite my work in a cleaner way.

An ideal timeline:

* A scratch mock as generic as possible
* Add as soon as possible few design patterns: logs, configuration, etc.
* Fork this repo for an advanced and generic REST API
* Add cool stuff (admin dashboard, app DB ORM, queues, workers, etc.)
* But **KEEP IT AS GENERIC AS POSSIBLE**...!

### Should i use this?

I think this repo would be usefull to fork if you are planning to write a project where you know you want to use Flask as REST API endpoint somewhere.

1. First you could write mocks for your interface to test
2. Then implement them with whatever you want as background middleware
    <small> e.g. FS (irods), graphDB (neo4j), whatever </small>

Note: if you plan to have a DB driven API, i think you should first take a look at the awesome project of [Python Eve](http://python-eve.org/) which works with Redis, MongoDB or SQLalchemy.

### What it will be based on

* Flask (*obviously*)
* Jinja2
* Flask Cors
* Flask Restful plugin (and evaluating Flask Classy, also)

**stil to be added**
* Tracestack
* Flask Security
    Simple RBAC + OAuth tokens + encryption + user registration
    + Mail + Login + Principal + Flask Admin interface
* Flask Cache
* Plumbum
* Flask Uploads
* Alembic? migrations for SQLalchemy

---

## Getting started

### Prerequisites

Install docker and docker-compose. For example:

```
# Install docker
curl -sSL https://get.docker.com/ | sh
# Install docker-compose
pip install -U docker-compose
```

### How to run

```
$ git clone https://github.com/pdonorio/rest-mock.git
$ cd rest-mock
$ docker-compose up
```

### How to test

You may test via command line with **wget** or **curl**.

```
curl -v http://localhost:8081/api/foo
```

To write a client with python i would suggest using `requests`.
To write a javascript client take a look at `Angularjs` and `Restangular` lib.

---

## How to add an endpoint

#### A quick way

Edit `mylibs/resources/exampleservices.py` and add a rest class:

* The class must extend `ExtendedApiResource`
* The class should use the decorator `@for_all_api_methods(standardata)`
* Provide at least the `get` method

The base code is found inside the `mylibs.resources.base` module. Please check the provided examples inside the module to write the right code.

**Test it**: if your class is called `MyClass`, it will be reachable at the address `http://HOST:PORT/api/myclass` address of the running server.
You can also specify a different address, by overiding the attribute `endpoint` of your class.

#### Cleaner way

Define a file `confs/endpoints.ini` with the following syntax:

```
[module_name]
class=endpoint
```

For example, after creating a file `myresource.py` inside `mylibs/resources`,
containing two classes `One` and `Two`, you could use:

```
[myresource]
One=foo
Two=hello/world
```

The system would provide the two following working URLs:

```
# Resource One
http://localhost:8081/api/foo
# Resource Two
http://localhost:8081/api/hello/world
```

Also as provided example of using a key with an endpoint
but getting a (programmatic) error response, you may test:
```
curl -v http://localhost:8081/api/hello/world/keyword
```

<small> Note: `localhost:8081` should change to your server ip and port.
The above example is based on running docker compose on linux.</small>

---

## Creator(s)

[Paolo D'Onorio De Meo](https://twitter.com/paolodonorio/)

## Copyright and license

Code and documentation copyright: `Paolo D'Onorio De Meo @2015`.

Code released under the [MIT license](LICENSE).
