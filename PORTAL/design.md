# The Design for the Benchmarking Job Queue Tooling

## Motivation

Measuring software performance is a delicate effort.  The execution
environment must be carefully controlled when benchmarking (or any
other measurement activity) if you want consistent, repeatable results.
So the target host must be carefully configured (e.g. CPU pinning)
and any extra load (e.g. background processes) must be minimized.
That includes not accidentally running the benchmarks multiple
times concurrently.

All of that can be tricky.  Doing it manually is manageable at first,
but it gets much harder if any of the following happens:

* there is more than one person involved
* there is more than one host (e.g. x64 vs. ARM, linux vs, Windows)
* a host is unreachable from your usual network
* your results set reaches a certain size
* you want to run benchmarks on a regular schedule
* you want any other sort of automation

Addressing all that is the motivation for this tool.  It also aims
to simplify sharing results publicly.

Note that the primary use case for the tool is to run Python benchmarks
using [pyperformance](https://github.com/python/pyperformance).
However, it is flexible enough to support running other
sorts of jobs (e.g. profiling).

## Overview

On the user-facing side, there is a CLI that wraps a client library,
which, in turn, wraps a network service that does/coordinates all the
work:

   `CLI -> client lib -> service -> (DB or worker or ...)`

The service provides (or will provide) the following functionality:

* a job queue, with support for running `pyperformance`
* results storage (filesystem)
* upload to a codespeed instance (e.g. speed.python.org)
* host management (basic setup, performance tuning)
* user management
* basic authentication

Keep in mind that the functionality is focused on what is needed
for running benchmarks, so don't expect it to be comprehensive
beyond that.

From a deployment standpoint, there are essentially 7 roles:

1. client
2. service
3. datastore
4. auth
5. job queue
6. worker
7. isolated worker (for performance-sensitive jobs)

There must be at least one worker for each target architecture/OS
for jobs where that matters.  Also, at least one regular worker
sits between the job queue and any isolated workers.

A minimal setup would have a single host filling all the roles.
A basic setup would be all the services on one host, a worker
running there, an isolated worker running on another host,
and the client being any host.

### API

```
Client(url, config)
    users: [User]
        (list, get, add, remove)
    hosts: [Host]
        (list, get, add, remove)
    jobs: [Job]
        (list, get, add, remove)
        current
    queue: [Job]
        (list, get, push, pop, move, remove)
        pause()
        unpause()
    results: [BenchmarksResult]
        (list, get, add, remove)

Entity(id, status, ...)
    modify()
    enable()
    disable()

User(Entity...)

Host(Entity...)
    configure()
    update()

Job(Entity...)
    run()
    attach()
    cancel()

BenchmarkResult(Entity...)
    read()
    write()
    upload()
    compare()
```

tasks:
* `build_cpython(...)`
* `run_benchmarks(buildid)`

### Open Questions

* use buildbot?
* use celery for the job queue?
* other results storage (e.g. GitHub repo, sqlite)?

### Future Possibilities

* other client options, e.g. web, GH action, bot
* support managing a codespeed instance>
* expanded host management (e.g. full configuration, installs, updates)?
* ...


## Details

* entities
    * `[user]`
    * `[host]`
    * `[job]`
    * `[result]`

### user-facing

* tools
    * `<CLI>`
    * (maybe later:  web client, GH action, bot)
* libraries
    * `(client lib)`
    * `(tasks lib)`  (~pyperformance)
* services
    * `_pyperformance_`

#### workflows

* `[user] -> <tool> -> (client lib) -> _pyperformance_`
* `[user] -> (client lib) -> _pyperformance_`
* `[user] -> (tasks lib)`


### internal

XXX Use buildbot?

* libraries
    * users lib
    * hosts lib
    * worker lib
* services
    * `_job queue_`
    * `_datastore_`
    * `_hosting_`
* entities
    * `[worker]`
    * `[isolated worker]`

#### workflows

managing users:
* `_pyperformance_ -> (users lib) -> _datastore_`

managing hosts:
* `_pyperformance_ -> (hosts lib) -> _datastore_`
* `_pyperformance_ -> (hosts lib) -> _hosting_`
* `_pyperformance_ -> (hosts lib) -> [host]`

managing jobs:
* `_pyperformance_ -> _job queue_ -> _datastore_`
* `_pyperformance_ -> _job queue_ -> _datastore_ -> [worker] -> _job queue_ -> _datastore_`

running jobs:
* `[worker] -> (tasks lib)`
* `[worker] -> (hosts lib) -> [isolated worker] -> (tasks lib)`


### auth

We will use some proven mechanism for authentication (and access control).
