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

Edit `mylibs/resources/mock.py` and add a rest class.
The class should contain at least the get method.
If you class is called `MyClass`, it will be reachable
at the `api/myclass` address of the web server.