Lacune Mémorielle Sociale (LMS) for Python
==========================================

`PyLMS` a command line tool to create and manage Persons and their Relationships.

WHY PyLMS
=========

It starts from a real problem
-----------------------------

This is the best reason and use case for a software, right? :-) 

My problem is that I have a long living issue to remember people names, history and relationships.

Certainly that could be improved (or fix!) with software, right?

Personal demo project for Python and other technologies
-------------------------------------------------------

I needed a topic for a personal project that would give me an opportunity to learn and/or improve (and demo) on:
* my practice of Python as a programming language and the Pythonic way (as a 20+ years Java developer)
* a bunch of technologies, frameworks, etc.
  * Graph databases, [`Flask`](https://flask.palletsprojects.com/en/3.0.x/), [`FastAPI`](https://fastapi.tiangolo.com/), ...
  * Machine Learning for Natural Language processing
  * ...
* a fun application life cycle
  * from a CLI POC
  * to a GUI application
  * to on-premises monolithic server
  * to a cloud-based micro-services-based online service
* coding practices:
   * project management with [tickets](https://linear.app/pylms/) and [pull requests](https://github.com/lesaint/PyLMS/pulls?q=is%3Apr+is%3Aclosed)
   * [hexagonal architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
   * contract testing
   * ...

Much more on the purpose and goals of this project and how I intend to run it [is available here](PROJECT_RATIONAL.md).

Install
=======

see [build](#how-to-build), [run and develop](#how-to-run-and-develop)

Usage
=====

* to list all Persons and Relationships: `pylms`
* to filter the above to a Person (or Persons) which first name and/or last name contain a specific word: `pylms john`
  * search is case-insensitive and accent-sensitive
* to create a Person `pylms create John Doe` or `pylms create John`
   * supports first name (single word) alone or first name and last name separated by a blank space 
* to create a relationship `pylms link John Doe père de Tony Doe` or `pylms link John père de Tony`
   * "père de" is an example of a Relationship alias and is looked up to tell apart the Persons in the linking request 
   * list of supported relationship alias defined [here](/src/pylms/core.py#L195)
* to delete a person `pylms delete John` or `pylms John`
* to update the firstname/lastname of a person `pylms update John`

Development
===========

Status
------

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=lesaint_PyLMS&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=lesaint_PyLMS)

Requirements
------------

* `Python3`
* `pip`
* `Tkinter` and `Tk`
  * on ubuntu, use `sudo apt-get install python3-tk` 
* `make`

How to build
------------

```shell
make build
```


How to run and develop
----------------------

1. see [build](#how-to-build)
2. run with:
    ```shell
    source .venv/bin/activate
    pylms
    ```

Code quality
------------

* code formatted with [`black`](https://black.readthedocs.io/en/stable/)
* unit tested with `unittest` and `pytest`
* code quality asserted with [SonarCloud](https://sonarcloud.io/project/overview?id=lesaint_PyLMS)

Licence
=======

GNU GENERAL PUBLIC LICENSE