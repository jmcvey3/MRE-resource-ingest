# Water Current at MCRL

TSDAT example ingest of raw ACDP data. 
Data is a clipping of a single ebb and flood tide from a 13 day deployment of a 
Nortek Signature 1000 in the inlet to Sequim Bay, part of a study on acoustic interference. 
Ingest requires the [dolfyn](https://github.com/jmcvey3/dolfyn) python package currently in development.

McVey J.R., and R.J. Cavagnaro. 2020. "ADCP Interference Raw Data." PNNL-SA-156985.

Corresponding dev: [James McVey](mailto:james.mcvey@pnnl.gov)


## Ingest Organization

The ingest takes the following layout:

- `runner.py` –– development entry point to run this pipeline on a set of input files.
- `mapping.py` –– Defines a mapping of filepath pattern to ingest specification so that
higher level processes know which ingest and configurations to use given a set of input
files.
- `__init__.py` –– Declares this folder as a Python module and provides a number of
methods / classes that upstream code can import.
upstream code can easily launch this ingest on data with the right parameters.
- `config/` –– Contains `yaml` configuration files for specifying metadata, quality
checks and handling, variable retrieval specifications, and input/output types.
- `pipeline/` –– Contains Python code meant to be modified to implement plotting
capabilities, add derived variables, implement custom `FileHandler` or qc objects, or
support any other custom functionality needed.
- `tests/` –– Contains tests that should be applied to this ingest in order to ensure
it functions as intended. Tests in here will be run any time a change is made to the
remote main branch, so the test(s) should be lightweight if possible.


## Getting started

1. Ensure that your development environment is set up according to
[the instructions](../../README.md#development-environment-setup).

2. Use the `TODO-Tree` VS Code extension or use the search tool to find occurances of
"`# TODO – Developer:`". Each instance of this requires your attention. Attend to all
of these TODOs and remove the "`TODO – Developer:`" text as you do so.

3. As you are developing, try to follow best practices to save yourself (and others)
time:
    - Commit your changes early, and make commits after each significant change.
    - Tests should be written as soon as possible, and you should test your code often.
    - Try to write clean and readable code that can be reused by others.
    - Document complexities such that future you and readers of this code understand
    what it is that you are doing.

4. You can run your code locally in VS Code by running the tests, or by 
running/debugging the `runner.py` script at the same level as this `README.md` file.

5. When you have finished the ingest script your tests should pass, the code should be
formatted by `black`, there should be no `flake8` warnings (Use "`# noqa`" to disable
a specific line, if need be), and this `README.md` file should be updated to include a
description of your ingest pipeline for end-users, project maintainers, and curious
onlookers who may not be familiar with your work. Additionally, please remove this
section ("Getting Started") of the README.md file. If this has all been completed, then
commit and push your changes to your repository, sync it up with the upstream main
repository, and submit a pull request so that your changes can be reviewed and merged
into production.
