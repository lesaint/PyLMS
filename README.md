LMS
=====

`LMS` is a motive to work on new stuff while providing a mean to cope with my personal difficulty to remember people's names and relationships.

`LMS` stands for "**L**acune **M**émorielle **S**ociale" (French for "Social Memory Gap").

> [!NOTE]
> Afaik. I invented the terms for "LMS" and "Lacune Mémorielle Sociale". Maybe the name and/or the problem is real thing, but I didn't search.

The high level idea
===================

When `LMS` hits me, the typical questions I ask myself look like:

* "Comment s'appelle le père de Paul?" (What is Paul's father name, already?")
* "Qui est la femme de Remi?" (Who is Remi's wife?)
* "Comment s'appellent les femmes de mon cours d'escalade" (What are the names of the women attending climbing class with me?)

These are basically queries on persons ("Paul", "Remi", "Pierre", "me"), relationships ("père de", "femme de", "femmes de"), and tags ("cours d'escalade").

So, let's build-up solutions and create applications, services, etc. around that.

LMS applications
================

`LMS` is made of several projects:

|            |                           |                                                                                                                    |                                        |
|:-----------|:--------------------------|--------------------------------------------------------------------------------------------------------------------|:--------------------------------------:|
| `PyLMS`    | a CLI and GUI in `Python` | to both create a [MVP](https://en.wikipedia.org/wiki/Minimum_viable_product) of `LMS` and further work with Python | [python/README.md](python/README.md)   |
| `AndroLMS` | an Android App            | because my phone is always at reach when `LMS` hits me and to explore both `Android` development and `Kotlin`      | [android/README.md](android/README.md) |


Learning through practice
=========================

As a consequence, this project has superb opportunities to learn:

 * I can start with a simple CLI and evolve the project to an auto-scaling SAAS service running in the Cloud, with both a web interface and an Android application.
 * I can start with a plain JSON file as a database and evolve to Graph Database and a search service supporting Natural Language requests with AI.
 * I can work on both the migrations between each of these steps and keeping them operational concurrently (e.g. the CLI can ultimately become a client to the SAAS service API).

Despite the technical potential, I want to balance it with:

1. functional purpose of the tool as the driver and decision maker of technical changes (i.e. no technical change without user value)
2. my professional centers of interest and my personal strengths: 
    * Deepen my knowledge in Python programming and the Python ecosystem (at some point, I prepared for [PCPP1](https://pythoninstitute.org/pcpp1) with this project)
    * Backend development (I can't deepen into Frontend as much #chooseYourBattles)
    * Application and Architecture design
    * Software Development best practices

Below, I keep track of this learning plan and its progress.

Python Programing
-----------------

* comply with the Zen of Python for [packages and modules](src/pylms), use [`__main__.py`](src/pylms/__main__.py)
* build best practices: `setuptools`, `wheel` (see [setup.cfg](setup.cfg))
* UI development with `tkinter` (PCPP1 certification preparation) (see [gui.py](src/pylms/gui.py))
* Testing with `pytest`, `unitest`, patching, mocks, fixtures for property testing (see [main_test.py](tests/pylms/main_test.py#L20-L43))
* Testing at scale with [Contract Testing](https://pactflow.io/blog/what-is-contract-testing/), [Chaos Testing](https://en.wikipedia.org/wiki/Chaos_engineering) 

Software Engineering best practices
-----------------------------------

* Code Quality: `Black`, `SonarCloud` analysis, [high test coverage](https://sonarcloud.io/summary/new_code?id=lesaint_PyLMS)
* Change management
    * issue tracking with [Linear](https://linear.app)
    * issues described as WHY-WHAT-HOW and as small steps of incremental value ([sample](https://github.com/lesaint/PyLMS/pull/24), [other samples](https://github.com/lesaint/PyLMS/pulls?q=is%3Apr+is%3Aclosed+HOW))
    * code updates with [Pull Requests](https://github.com/lesaint/PyLMS/pulls)
* Continuous Integration: `GitHub actions`

> [!NOTE]
> I selected Linear to explore an innovative approach to issue tracking compared to Jira. Unfortunately, it's private.
> As a workaround, description of [Pull Requests](https://github.com/lesaint/PyLMS/pulls?q=is%3Apr+is%3Aclosed) reproduces the content of issues.

Software Design
---------------

* Implement a [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
  * in a monolith: [do it in Python](https://github.com/lesaint/PyLMS/pull/13), and [prove it by adding UI without a change to the core](https://github.com/lesaint/PyLMS/pull/27/files)
  * in a system

Licence
=======

GNU GENERAL PUBLIC LICENSE (GPL)
