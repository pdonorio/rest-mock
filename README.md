# rest-mock

The **base** for my *REST API* projects:

A python 3 Flask server mapping classes into mock API end-points.

## Prerequisites

Install docker and docker-compose. For example:

```
# Install docker
curl -sSL https://get.docker.com/ | sh
# Install docker-compose
pip install -U docker-compose
```

## How to run

```
$ git clone https://github.com/pdonorio/rest-mock.git
$ cd rest-mock
$ docker-compose up
```

## How to test

```
curl http://localhost:8081/api/foo
```

## How to add an endpoint

**Quick way**:

Edit `mylibs/resources/mock.py` and add a rest class.
The class should contain at least the get method.
If you class is called `MyClass`, it will be reachable
at the `api/myclass` address of the web server.

You can specify a different address overiding the attribute `endpoint` inside
the class.

**Cleaner way**:

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
