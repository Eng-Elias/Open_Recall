# Open_Recall CLI

Open_Recall provides a command-line interface (CLI) that allows you to interact with the application directly from your terminal.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/Eng-Elias/Open_Recall)

## Installation

After installing the Open_Recall package, the `open_recall` command will be available in your terminal:

```bash
pip install open-recall-cli
```

## Available Commands

### Start the Server

Start the Open_Recall server with optional configuration:

```bash
open_recall server [--host HOST] [--port PORT] [--no-browser]
```

Options:

- `--host`: Specify the host to bind the server to (default: from config or 127.0.0.1)
- `--port`: Specify the port to bind the server to (default: from config or 8742)
- `--no-browser`: Don't open a browser window automatically

### Launch Desktop Application

Start the Open_Recall desktop application powered by Toga:

```bash
open_recall desktop
```

This will launch the full desktop application with a native UI.

### Show Version

Display the current version of Open_Recall:

```bash
open_recall version
```

## Environment Variables

Open_Recall CLI respects the following environment variables:

- `OPEN_RECALL_HOST`: Host to bind the server to
- `OPEN_RECALL_PORT`: Port to bind the server to

## Examples

Start the server on a custom port:

```bash
open_recall server --port 9000
```

Start the server without opening a browser:

```bash
open_recall server --no-browser
```

## Development

For development purposes, you can also run the CLI directly from the source code:

```bash
# Install in development mode
pip install -e .

# Run CLI commands
python -m open_recall
```

## Related Documentation

For more information about Open_Recall, see the [main README](../README.md) file.
