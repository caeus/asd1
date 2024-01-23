# ASD
ASD is a build system for monorepos. It emerges from the need to address these pain points:

* Poor monorepo support for very mainstream languages like JS, Python.
* No Turing complete languages to declare builds (TOML, YAML, JSON). Which makes it a pain in the ass to DRY builds.
* Bazel's frustratringly complex model, and how bad it plays with others.

ASD also draws inspiration from other build systems, especially those which model tasks and dependencies as DAG (Bazel (I KNOW), Gradle, SBT, Pants, Makefile).

## Philosphy

Reproducible, isolated, hermetic builds! NO! Man, that's important, sure, but not as important as allowing developers to partially adopt. So ASD lets you use whatever traditional dependency manager you are used to (pip, poetry, yarn, npm, who cares?), while it provides the toolkit to organize task execution over your monorepo.

### Terminology
As such, and trying no to make it super difficult to learn, we use a language inspired in all those tools.
Our unit of work is a Task, and a Task is an implementation, and a set of dependencies (references to other tasks)

Task reference is determined by its location, which takes us to a package. A package is a collection of tasks under a namespace. Multiple packages inhabit a project.

A project is a collection of packages, and it's bound to a folder inside the workspace/monorepo. Projects are declared in files named `__project__.py`.

The workspace is but the root of the monorepo, and it's declared using the file `<monorepo_root>/__workspace__.py`.

Similar to Bazel, but simpler! no toolchains, no remote repositories, none of that.

## Usual anatomy of an ASD monorepo

ASD is written using Python, so a lot of the cognitive overhead comes from the python development intrincacies.

As such, and to have some sort of hermeticness, isolation and reproducibility, the `__workspace__` file controls the creation of the virtual env to interpret any of the `__project__.py` files.

That env, can be anything,

