# Open_Recall

<p align="center">
  <img src="open_recall/static/images/logo.png" alt="Open_Recall Logo" width="200">
</p>

## Overview

Open_Recall is a powerful desktop application that helps you search, find and analyze anything you've seen on your PC. Using advanced search capabilities, you can easily locate past activities, documents, applications, and websites based on your memory fragments or timeline navigation.

<p align="center">
  <a href="https://youtu.be/mqYihFedxmY">
    <img src="https://img.youtube.com/vi/mqYihFedxmY/0.jpg" alt="Open_Recall Demo Video" width="600">
  </a>
</p>
<p align="center">
  <a href="https://youtu.be/mqYihFedxmY">Watch the Open_Recall Demo on YouTube</a>
</p>

<p align="center">
  <a href="https://medium.com/@eng_elias/open-recall-my-open-source-solution-for-remembering-everything-youve-seen-on-the-pc-ab3976add3d0">
    <img src="https://img.shields.io/badge/Medium-Read%20the%20Article-black?style=for-the-badge&logo=medium" alt="Medium Article">
  </a>
</p>

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/Eng-Elias/Open_Recall)

## Project Structure

```
.
├── open_recall/           # Python package
│   ├── app.py             # Toga desktop app entry point
│   ├── cli.py             # Command-line interface
│   ├── main.py            # FastAPI application
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   └── utils/             # Utility modules
├── pyproject.toml         # Python project configuration
├── setup.py               # Package setup configuration
├── requirements.txt       # Python dependencies
├── Makefile               # Development and build commands
└── README.md              # This file
```

## TO DO List

- [x] web app
- [x] desktop app
- [x] CLI app
- [ ] contribution guide
- [ ] git hooks (for code formating and linting)
- [ ] customize the installer file
- [ ] installer files for different platforms

## Installation Options

Open_Recall can be installed and used in two ways:

### 1. Windows Desktop Application

For the best user experience with a native GUI:

1. Download the latest Windows installer from the [Releases page](https://github.com/Eng-Elias/Open_Recall/releases)
2. Run the installer and follow the on-screen instructions
3. Launch Open_Recall from your Start Menu or Desktop shortcut

### 2. Python Package (All Platforms)

For cross-platform usage or integration with other tools:

```bash
pip install open-recall-cli
```

After installation, you can use the `open_recall` command-line interface:

```bash
# Start the desktop application
open_recall desktop

# Start the server only
open_recall server

# Show version information
open_recall version
```

For more details on CLI usage, see [CLI Documentation](open_recall/CLI.md).

## Configuration

Open_Recall uses port 8742 by default to avoid conflicts with other applications. You can change this in two ways:

1. Set the `OPEN_RECALL_PORT` environment variable:

   ```bash
   # Windows
   set OPEN_RECALL_PORT=9000

   # Linux/macOS
   export OPEN_RECALL_PORT=9000
   ```

2. Edit the `config.json` file in the application directory:
   ```json
   {
     "app": {
       "port": 9000,
       "host": "localhost",
       "debug": false
     }
   }
   ```

Other configuration options:

- `OPEN_RECALL_HOST`: Change the host interface (default: localhost)
- `OPEN_RECALL_DEBUG`: Enable debug mode (set to "true")

## Development

### Setup Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/Eng-Elias/Open_Recall.git
   cd Open_Recall
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:

   ```bash
   make install-dev
   # or
   pip install -e .
   ```

### Available Make Commands

The project includes a Makefile with useful commands for development and packaging:

```bash
# Run the desktop application in development mode
make run_desktop

# Run the web server with hot reloading
make run_web_dev

# Build the desktop application with Briefcase
make build_desktop

# Package the application as a Windows installer
make package_desktop

# Install the package in development mode
make install_dev

# Build the Python package for PyPI
make pypi_build

# Upload the package to PyPI
make pypi_upload

# Clean build artifacts
make clean
```

## Packaging and Distribution

### Desktop Application (Windows)

To create a standalone Windows installer:

```bash
make package_desktop
```

The packaged installer will be available in the `dist` directory.

### Python Package (PyPI)

To build and publish the Python package to PyPI:

```bash
make pypi-upload
```

## Support

If you find Open_Recall helpful and would like to support its development, consider buying me a book! Your support will allow me to dedicate more time to enhancing and adding new features to Open_Recall.

[https://www.buymeacoffee.com/eng_elias](https://www.buymeacoffee.com/eng_elias)

[![Buy Me a Coffee](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeW41NXV3ZXYxY2pvOG5lcjJueDF3NDFlcWNneDJ4MW9kY25jbWhzeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/7kZE0z52Sd9zSESzDA/giphy.gif)](https://www.buymeacoffee.com/eng_elias)

## License

This application is open-source and is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for details.

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
