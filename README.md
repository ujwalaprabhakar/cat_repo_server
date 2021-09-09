# Ujcatapi

Welcome to Lionbridge AI Cat Management Service.

## Quickstart Guide

You can start a local instance of Ujcatapi by running:

```sh
    make up
```

You will see the logs in your terminal window. Once all images are built, containers running, and
migrations run, you will see log line "Application startup complete." You can open your browser to
http://localhost:10000 to see the docs and play with the API.

You can run the complete test suite on a separate, test database by:

```sh
    make test
```

`make test` is meant to rerun all database migrations on every test run to be idempotent and not
depend on other commands. If you find this too slow for your development work, you can run tests
in TDD mode:

```sh
    make tdd
```

This will migrate your test database once and rerun all unit tests on every source code change, so
that you get an almost immediate feedback on your changes.

`make up` and `make tdd` are compatible and can be run at the same time. You can run `make up`
in one tab of your terminal and `make tdd` in other tab of your terminal to be able to immediately
see the changes you are introducing as well as the results of the unit tests.

Once you are done, you can bring everything down by:

```sh
    make down
```

If you want to remove Ujcatapi Docker containers, images, and volumes (this will delete your local
database) you can do so by:

```sh
    make rm
```

For more information, continue reading this readme and also read the documentation in /docs folder,
e.g. docs/testing.md to know more about our testing strategy.

## Advanced Guide

### Running on Non-Standard Port

By default the service will be exposed on port 10000, but you can change by passing the APP_PORT
var to make up:

```sh
    make up APP_PORT=12001
```

### Building and Rebuilding Images

For development work, `make up` (documented above) will make sure that the newest image is built
and available, but if you want to build images without starting containers or running database
migrations, you can simply do:

```sh
    make build
```

If you want to force a rebuild without using cache, you can do:

```she
    make rebuild
```

### Running Migrations

For development work, `make up` (documented above) will make sure that all migrations are run on
your local development database; and `make test` will make sure that all migrations are run on
your local test database, but if you want to run migrations yourself, you can do:

```sh
    make migrate
```

If you want to delete all objects from your local dev database, you can do so by:

```sh
    make delete_collections
```

the next time you run `make up` after deleting collections, you will see a migrated database with
just the default objects inserted.

### Running Tests

While `make test` will run the complete test suite on a separate, fully migrated test database,
the following commands might enable you to benefit from a faster test-driven feedback loop.

You can run just the unit tests on the mounted codebase and a test database by:

```sh
    make test-unit
```

You can run just the mypy type checks on the mounted codebase (this does not require a database)
by:

```sh
    make test-type
```

You can run just the style (flake8) checks on the mounted codebase (this does not require
a database) by:

```sh
    make test-style
```

You can run just the formatter (black) checks on the mounted codebase (this does not require
a database) by:

```sh
    make test-format
```

If you find any formatting errors you would like to have fixed automatically, you can run:

```sh
    make test-format-fix
```

You can generate test coverage report by:

```sh
    make test-coverage
```

By default, code with test coverage under 95% will not pass CI/CD checks.

### Get into the container

If you need to get into the container of the application server, run:

```sh
    make bash
```

and if you need bash inside the database container, run:

```sh
    make bash-mongodb
```
