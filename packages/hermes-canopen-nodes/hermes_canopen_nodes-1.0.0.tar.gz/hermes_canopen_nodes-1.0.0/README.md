# Hermes canopen nodes
[![PyPI version](https://badge.fury.io/py/hermes-canopen-nodes.svg)](https://pypi.org/project/hermes-canopen-nodes)

A collection of nodes to interface with canopen.

## Installation

### From PyPI

Install the package directly from PyPI using pip:

```bash
pip install hermes-canopen-nodes
```

### From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/node-hermes/hermes-canopen-nodes
pip install -e hermes-canopen-nodes
```

## Development

This project depends on UV for managing dependencies.
Make sure you have UV installed and set up in your environment.

You can find more information about UV [here](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv venv
```

```bash
uv sync --all-extras --dev
```
