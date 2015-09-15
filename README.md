# rest-mock

The **base** for my *REST API* projects:

A Flask python server with Mock configurable endpoints
mapped to class code.

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
