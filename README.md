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

You may test via command line with **wget** or **curl**.

```
curl -v http://localhost:8081/api/foo
```

To write a client with python i would suggest using `requests`.
To write a javascript client take a look at `Angularjs` and `Restangular` lib.

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