pytask-julia
============

.. image:: https://img.shields.io/pypi/pyversions/pytask-julia
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/pytask-julia

.. image:: https://img.shields.io/conda/vn/conda-forge/pytask-julia.svg
    :target: https://anaconda.org/conda-forge/pytask-julia

.. image:: https://img.shields.io/conda/pn/conda-forge/pytask-julia.svg
    :target: https://anaconda.org/conda-forge/pytask-julia

.. image:: https://img.shields.io/pypi/l/pytask-julia
    :alt: PyPI - License
    :target: https://pypi.org/project/pytask-julia

.. image:: https://img.shields.io/github/workflow/status/pytask-dev/pytask-julia/main/main
    :target: https://github.com/pytask-dev/pytask-julia/actions?query=branch%3Amain

.. image:: https://readthedocs.org/projects/pytask-julia/badge/?version=latest
    :target: https://pytask-julia.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/pytask-dev/pytask-julia/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/pytask-dev/pytask-julia

.. image:: https://results.pre-commit.ci/badge/github/pytask-dev/pytask-julia/main.svg
    :target: https://results.pre-commit.ci/latest/github/pytask-dev/pytask-julia/main
    :alt: pre-commit.ci status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black


Installation
------------

pytask-julia is available on `PyPI <https://pypi.org/project/pytask-julia>`_ and
`Anaconda.org <https://anaconda.org/conda-forge/pytask-julia>`_. Install it with

.. code-block:: console

    $ pip install pytask-julia

    # or

    $ conda install -c conda-forge pytask-julia

You also need to have Julia installed and ``julia`` on your command line. Test it by
typing the following on the command line

.. code-block:: console

    $ julia -h

If an error is shown instead of a help page, you can install Julia on Unix systems with

.. code-block:: console

    $ conda install -c conda-forge julia

or choose one of the installers on this `page <https://julialang.org/downloads/>`_.


Usage
-----

Similarly to normal task functions which execute Python code, you define tasks to
execute scripts written in Julia with Python functions. The difference is that the
function body does not contain any logic, but the decorator tells pytask how to handle
the task.

Here is an example where you want to run ``script.julia``.

.. code-block:: python

    import pytask


    @pytask.mark.julia
    @pytask.mark.depends_on("script.jl")
    @pytask.mark.produces("out.csv")
    def task_run_jl_script():
        pass

Note that, you need to apply the ``@pytask.mark.julia`` marker so that pytask-julia
handles the task.

If you are wondering why the function body is empty, know that pytask-julia replaces the
body with a predefined internal function. See the section on implementation details for
more information.


Multiple dependencies and products
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What happens if a task has more dependencies? Using a list, the Julia script which
should be executed must be found in the first position of the list.

.. code-block:: python

    @pytask.mark.julia
    @pytask.mark.depends_on(["script.jl", "input.csv"])
    @pytask.mark.produces("out.csv")
    def task_run_jl_script():
        pass

If you use a dictionary to pass dependencies to the task, pytask-julia will, first, look
for a ``"source"`` key in the dictionary and, secondly, under the key ``0``.

.. code-block:: python

    @pytask.mark.julia
    @pytask.mark.depends_on({"source": "script.jl", "input": "input.csv"})
    def task_run_jl_script():
        pass


    # or


    @pytask.mark.julia
    @pytask.mark.depends_on({0: "script.jl", "input": "input.csv"})
    def task_run_jl_script():
        pass


    # or two decorators for the function, if you do not assign a name to the input.


    @pytask.mark.julia
    @pytask.mark.depends_on({"source": "script.jl"})
    @pytask.mark.depends_on("input.csv")
    def task_run_jl_script():
        pass


Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

The decorator can be used to pass command line arguments to ``julia``. An important
detail is that you need to differentiate between options passed to the Julia executable
and arguments passed to the script.

First, pass options to the executable, then, use ``"--"`` as a separator, and after that
arguments to the script.

The following shows how to pass both with the decorator.

.. code-block:: python

    @pytask.mark.julia(("--threads", "2", "--", "value"))
    @pytask.mark.depends_on("script.jl")
    @pytask.mark.produces("out.csv")
    def task_run_jl_script():
        pass

And in your ``script.jl``, you can intercept the value with

.. code-block:: Julia

    arg = ARGS[1]  # holds ``"value"``

If you pass only of of them, either options for the executable or arguments to the
script, you still need to include the separator.

.. code-block:: python

    @python.mark.julia(("--verbose", "--"))  # for options for the executable.
    def task_func():
        ...


    @python.mark.julia(("--", "value"))  # for arguments for the script.
    def task_func():
        ...


Parametrization
~~~~~~~~~~~~~~~

You can also parametrize the execution of scripts, meaning executing multiple Julia
scripts as well as passing different command line arguments to the same Julia script.

The following task executes two Julia scripts which produce different outputs.

.. code-block:: python

    from src.config import BLD, SRC


    @pytask.mark.julia
    @pytask.mark.parametrize(
        "depends_on, produces",
        [(SRC / "script_1.jl", BLD / "1.csv"), (SRC / "script_2.jl", BLD / "2.csv")],
    )
    def task_execute_julia_script():
        pass

And the Julia script includes something like

.. code-block:: julia

    produces = ARGS[1]  # holds the path

If you want to pass different command line arguments to the same Julia script, you
have to include the ``@pytask.mark.julia`` decorator in the parametrization just like
with ``@pytask.mark.depends_on`` and ``@pytask.mark.produces``.

.. code-block:: python

    @pytask.mark.depends_on("script.jl")
    @pytask.mark.parametrize(
        "produces, julia",
        [
            (BLD / "output_1.csv", ("--", "1")),
            (BLD / "output_2.csv", ("--", "2")),
        ],
    )
    def task_execute_julia_script():
        pass


Configuration
-------------

If you want to change the name of the key which identifies the Julia script, change the
following default configuration in your pytask configuration file.

.. code-block:: ini

    julia_source_key = source


Implementation Details
----------------------

The plugin is a convenient wrapper around

.. code-block:: python

    import subprocess

    subprocess.run(["julia", "script.jl"], check=True)

to which you can always resort to when the plugin does not deliver functionality you
need.

It is not possible to enter a post-mortem debugger when an error happens in the Julia
script or enter the debugger when starting the script. If there exists a solution for
that, hints as well as contributions are highly appreciated.


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
