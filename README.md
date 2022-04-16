# pytask-julia

[![PyPI](https://img.shields.io/pypi/v/pytask-julia?color=blue)](https://pypi.org/project/pytask-julia)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytask-julia)](https://pypi.org/project/pytask-julia)
[![image](https://img.shields.io/conda/vn/conda-forge/pytask-julia.svg)](https://anaconda.org/conda-forge/pytask-julia)
[![image](https://img.shields.io/conda/pn/conda-forge/pytask-julia.svg)](https://anaconda.org/conda-forge/pytask-julia)
[![PyPI - License](https://img.shields.io/pypi/l/pytask-julia)](https://pypi.org/project/pytask-julia)
[![image](https://img.shields.io/github/workflow/status/pytask-dev/pytask-julia/main/main)](https://github.com/pytask-dev/pytask-julia/actions?query=branch%3Amain)
[![image](https://codecov.io/gh/pytask-dev/pytask-julia/branch/main/graph/badge.svg)](https://codecov.io/gh/pytask-dev/pytask-julia)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pytask-dev/pytask-julia/main.svg)](https://results.pre-commit.ci/latest/github/pytask-dev/pytask-julia/main)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

______________________________________________________________________

Run Julia scripts with pytask.

## Installation

pytask-julia is available on [PyPI](https://pypi.org/project/pytask-julia) and
[Anaconda.org](https://anaconda.org/conda-forge/pytask-julia). Install it with

```console
$ pip install pytask-julia

# or

$ conda install -c conda-forge pytask-julia
```

You also need to have Julia installed and `julia` on your command line. Test it by
typing the following on the command line

```console
$ julia -h
```

If an error is shown instead of a help page, you can install Julia on Unix systems with

```console
$ conda install -c conda-forge julia
```

or choose one of the installers on this [page](https://julialang.org/downloads/).

## Usage

To create a task which runs a Julia script, define a task function with the
`@pytask.mark.julia` decorator. The `script` keyword provides an absolute path or path
relative to the task module to the Julia script.

```python
import pytask


@pytask.mark.julia(script="script.jl")
@pytask.mark.produces("out.csv")
def task_run_jl_script():
    pass
```

If you are wondering why the function body is empty, know that pytask-julia replaces the
body with a predefined internal function. See the section on implementation details for
more information.

### Dependencies and Products

Dependencies and products can be added as with a normal pytask task using the
`@pytask.mark.depends_on` and `@pytask.mark.produces` decorators. which is explained in
this
[tutorial](https://pytask-dev.readthedocs.io/en/stable/tutorials/defining_dependencies_products.html).

### Accessing dependencies and products in the script

To access the paths of dependencies and products in the script, pytask-julia stores the
information by default in a `.json` file. The path to this file is passed as a
positional argument to the script. Inside the script, you can read the information.

```julia
import JSON

path_to_json = ARGS[1]  # Contains the path to the .json file.

config = JSON.parse(read(path_to_json, String))  # A dictionary.

config["produces"]  # Is the path to the output file "../out.csv".
```

The `.json` file is stored in the same folder as the task in a `.pytask` directory.

To parse the JSON file, you need to install
[JSON.jl](https://github.com/JuliaIO/JSON.jl).

You can also pass any other information to your script by using the `@pytask.mark.task`
decorator.

```python
@pytask.mark.task(kwargs={"number": 1})
@pytask.mark.julia(script="script.jl")
@pytask.mark.produces("out.csv")
def task_run_jl_script():
    pass
```

and inside the script use

```julia
config["number"]  # Is 1.
```

### Debugging

In case a task throws an error, you might want to execute the script independently from
pytask. After a failed execution, you see the command which executed the Julia script in
the report of the task. It looks roughly like this

```console
$ julia <options> -- script.jl <path-to>/.pytask/task_py_task_example.json
```

### Managing Julia environments

Julia has support for environments to execute your tasks via `Pkg.jl` which is explained
[here](https://pkgdocs.julialang.org/v1/environments/).

pytask-julia allows you define a default environment via your
[pytask configuration file](https://pytask-dev.readthedocs.io/en/stable/tutorials/configuration.html).

Use the `julia_project` key to define an absolute path or a path relative to your
configuration file to point to your environment.

Probably your environment files `Manifest.toml` and `Project.toml` reside at the root of
your project folder as well as your pytask configuration file. Then, the content will
look like this.

```toml
[tool.pytask.ini_options]
julia_project = "."
```

You can also define environments for each task which will overwrite any other default
with the `project` keyword argument. Pass an absolute path or a path relative to the
task module.

```python
@pytask.mark.julia(script="script.jl", project=".")
@pytask.mark.produces("out.csv")
def task_run_jl_script():
    pass
```

### Command Line Options

Command line options can be pass via the `options` keyword argument.

```python
@pytask.mark.julia(script="script.jl", options=["--threads", "2"])
@pytask.mark.produces("out.csv")
def task_run_jl_script():
    pass
```

This example will execute the script using to threads.

### Repeating tasks with different scripts or inputs

You can also repeat the execution of tasks, meaning executing multiple Julia scripts or
passing different command line arguments to the same Julia script.

The following task executes two Julia scripts, `script_1.jl` and `script_2.jl`, which
produce different outputs.

```python
for i in range(2):

    @pytask.mark.task
    @pytask.mark.julia(script=f"script_{i}.jl")
    @pytask.mark.produces(f"out_{i}.csv")
    def task_execute_julia_script():
        pass
```

If you want to pass different inputs to the same Julia script, pass these arguments with
the `kwargs` keyword of the `@pytask.mark.task` decorator.

```python
for i in range(2):

    @pytask.mark.task(kwargs={"i": i})
    @pytask.mark.julia(script="script.jl")
    @pytask.mark.produces(f"output_{i}.csv")
    def task_execute_julia_script():
        pass
```

and inside the task access the argument `i` with

```julia
import JSON

path_to_json = ARGS[1]  # Contains the path to the .json file.

config = JSON.parse(read(path_to_json, String))  # A dictionary.

config["produces"]  # Is the path to the output file "../output_{i}.csv".

config["i"]  # Is the number.
```

### Serializers

You can also serialize your data with any other tool you like. By default, pytask-julia
also supports YAML (if PyYaml is installed).

Use the `serializer` keyword arguments of the `@pytask.mark.julia` decorator with

```python
@pytask.mark.julia(script="script.jl", serializer="yaml")
def task_example():
    ...
```

And in your Julia script use

```julia
import YAML
config = YAML.load_file(ARGS[1])
```

Note that the `YAML` package needs to be installed.

If you need a custom serializer, you can also provide any callable to `serializer` which
transforms data to a string. Use `suffix` to set the correct file ending.

Here is a replication of the JSON example.

```python
import json


@pytask.mark.julia(script="script.jl", serializer=json.dumps, suffix=".json")
def task_example():
    ...
```

### Configuration

You can influence the default behavior of pytask-julia with some configuration values.
Place them into a `pyproject.toml` file.

**`julia_serializer`**

Use this option to change the default serializer.

```toml
[tool.pytask.ini_options]
julia_serializer = "json"
```

**`julia_suffix`**

Use this option to set the default suffix of the file which contains serialized paths to
dependencies and products and more.

```toml
[tool.pytask.ini_options]
julia_suffix = ".json"
```

**`julia_options`**

Use this option to set default options for each task which are separated by whitespace.

```toml
[tool.pytask.ini_options]
julia_options = ["--threads", 2]
```

**`julia_project`**

Use this option to set a default environment for each task. Use either a path relative
to the configuration file or an absolute path. If your environment with `Manifest.toml`
and `Project.toml` is defined in the same directory as the configuration file
`pyproject.toml`, just use a dot.

```toml
[tool.pytask.ini_options]
julia_project = "."
```

If the environment files were in a folder next to the configuration file called
`environment` use

```toml
[tool.pytask.ini_options]
julia_project = "environment"
```

## Changes

Consult the [release notes](CHANGES.md) to find out about what is new.
