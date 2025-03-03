# Yandex Cloud Functions Tools

[![PyPI](https://img.shields.io/pypi/v/ycf-tools)](https://pypi.org/project/ycf-tools/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ycf-tools)](https://pypi.org/project/ycf-tools/)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=rocshers_ycf-tools&metric=coverage)](https://sonarcloud.io/summary/new_code?id=rocshers_ycf-tools)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=rocshers_ycf-tools&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=rocshers_ycf-tools)

[![Downloads](https://static.pepy.tech/badge/ycf-tools)](https://pepy.tech/project/ycf-tools)
[![GitLab stars](https://img.shields.io/gitlab/stars/rocshers/python/ycf-tools)](https://gitlab.com/rocshers/python/ycf-tools)
[![GitLab last commit](https://img.shields.io/gitlab/last-commit/rocshers/python/ycf-tools)](https://gitlab.com/rocshers/python/ycf-tools)

## Functionality

- Support for type hints
- Wrapper for convenient request `handling`
- Sentry integration

## Installation

`pip install ycf-tools`

or add `ycf-tools` in `requirements.txt`

## Quick start

```python
# module.py

from ycf import YcfServer, Context, HttpRequest

class Server(YcfServer):
    async def http_request_handler(self, context: Context, request: HttpRequest):
        return 'OK'
    

server = Server()

# entrypoint -> module.server
```

## Contribute

Issue Tracker: <https://gitlab.com/rocshers/python/ycf-tools/-/issues>  
Source Code: <https://gitlab.com/rocshers/python/ycf-tools>

Before adding changes:

```bash
make install-dev
```

After changes:

```bash
make format test test-go test-python
```
