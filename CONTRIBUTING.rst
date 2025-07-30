==============================
Contributing to OpenStack MCP Server
==============================

About the Project
==================

OpenStack MCP Server is a project that integrates various OpenStack functionalities with the Model Context Protocol (MCP), enabling LLM-powered management of OpenStack resources.

How to Contribute
=================

First, thank you for reading this document to contribute to our OpenStack MCP Server project. The following content explains the guidelines for contributing to our project, how to set up the development environment, and coding style guidelines.

PR Guidelines
=============

Issue Report
------------

Before submitting code for new features (and this also applies to some complex bug fixes), please first raise a **Feature request** or **Bug report**.

Review Process
--------------

- This project currently uses main and develop branches as the base. PRs to the main branch are restricted to the develop branch.
- All patches must be first merged into the develop branch and require approval from at least 2 code reviewers to be merged into develop.

Commit Message
--------------

We use the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ convention for writing commit messages.

Format::

    <type>[optional scope]: <description>
    [optional body]
    [optional footer(s)]

**Example**::

    feat(nova): implement server management tools

    Add Nova server listing and detail retrieval functionality
    for MCP clients with proper error handling and OpenStack SDK integration.

    - Add get_nova_servers tool
    - Add get_server_details tool  
    - Implement server status filtering
    - Add comprehensive error handling

    Closes #123

Development Environment
=======================

The following content is a guide for contributors to set up a development environment in their local environment.

Prerequisites
=============

- This project uses uv to manage Python packages. Please set up an environment where you can use uv in your local environment for development environment setup. `Reference <https://docs.astral.sh/uv/getting-started/installation/>`_
- We use ``python3.10`` as the default version. This is to ensure compatibility with other OpenStack projects.

UV Package Build
----------------

.. code-block:: bash

    uv sync --all-groups

Pre-commit
----------

Code style is managed uniformly through ruff. We recommend setting up pre-commit hooks so that auto-formatting is applied at the commit stage.

.. code-block:: bash

    pre-commit install

Testing
=======

Unit Tests
----------

All patches related to feature additions must implement unit test code. This project uses Pytest as the testing library, and if the project has been built successfully, you can run tests with the following command:

.. code-block:: bash

    uv run pytest