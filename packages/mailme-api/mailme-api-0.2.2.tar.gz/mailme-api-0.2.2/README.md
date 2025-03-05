# [Mailme API](http://mailme-api.hive.pt)

**Mailme API is a Python client library that provides a simple and convenient interface for interacting with the Mailme email gateway service.** With this client, developers can seamlessly send emails, manage recipients, and integrate [Mailme](http://mailme.hive.pt) into their Python-based applications with minimal setup.

## Description

Mailme API simplifies the process of sending emails programmatically by offering a Python-based interface to the [Mailme](http://mailme.hive.pt) service. It abstracts the underlying HTTP API into a Pythonic syntax, making it easier to implement and integrate email-sending functionality into your projects.

The library supports key features of the [Mailme](http://mailme.hive.pt) service, such as:

- **Authentication**: Secure your requests with a secret API key.
- **Customizable Email Content**: Define recipients, subject lines, and HTML or plain text email content.
- **Environment Variable Configuration**: Easily manage settings through environment variables for flexibility across different deployment environments.
- **Streamlined Email Sending**: Quickly send emails with minimal boilerplate code.

This API client is particularly useful for Python developers who need a reliable way to send notifications, reports, or other automated emails without diving into the complexities of SMTP servers or manual REST API calls.

### Key Benefits

- **Ease of Use**: A straightforward interface for sending emails with a few lines of code.
- **Flexibility**: Supports customizable email parameters, including multiple recipients and formatted content.
- **Seamless Integration**: Designed to fit naturally into Python applications and scripts.
- **Open Source**: Fully open-sourced under the Apache License 2.0, encouraging collaboration and contributions.

## Configuration

| Name                | Type  | Default                          | Description                                             |
| ------------------- | ----- | -------------------------------- | ------------------------------------------------------- |
| **MAILME_BASE_URL** | `str` | `https://mailme.bemisc.com/api/` | The base URL for the Mailme API requests.               |
| **MAILME_KEY**      | `str` | `None`                           | The secret key to be used to authenticate API requests. |

## Installation

```bash
pip install mailme-api
```

## Usage

```bash
RECEIVERS="receiver@domain.com" \
CONTENTS="Hello World" \
python -m mailme.scripts.sender
```

## License

Mailme API is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://github.com/hivesolutions/mailme-api/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/mailme-api/actions)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/mailme-api/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/mailme-api?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/mailme-api.svg)](https://pypi.python.org/pypi/mailme-api)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
