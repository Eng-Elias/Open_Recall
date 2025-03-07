# Open_Recall

## Overview

Open_Recall is a powerful desktop application that helps you search, find and analyze anything you've seen on your PC. Using advanced search capabilities, you can easily locate past activities, documents, applications, and websites based on your memory fragments or timeline navigation.

## Project Structure

```
.
├── electron/          # Electron main process
│   └── main.js       # Electron entry point
├── open_recall/      # Python package
│   ├── app.py        # Toga app entry point
│   ├── main.py       # FastAPI application
│   ├── static/       # Static files
│   │   └── js/
│   │       └── App.js # React components
│   └── templates/
│       └── index.html # Main template
├── pyproject.toml    # Python project configuration for Briefcase
├── requirements.txt  # Python dependencies
├── package.json     # Node.js dependencies
└── README.md         # This file
```

## Installation

### Using the Installer

1. Download the latest installer from the Releases page
2. Run the installer and follow the on-screen instructions
3. Launch Open_Recall from your Start Menu or Desktop shortcut

### Configuration

Open_Recall uses port 8742 by default to avoid conflicts with other applications. You can change this in two ways:

1. Set the `OPENRECALL_PORT` environment variable:
   ```
   # Windows
   set OPENRECALL_PORT=9000
   
   # Linux/macOS
   export OPENRECALL_PORT=9000
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
- `OPENRECALL_HOST`: Change the host interface (default: localhost)
- `OPENRECALL_DEBUG`: Enable debug mode (set to "true")

### Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/Eng-Elias/Open_Recall.git
   cd Open_Recall
   ```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:

```bash
npm install
```

4. Install development dependencies:
   ```
   pip install briefcase
   ```

5. Run the app in development mode:
   ```
   python -m open_recall.app
   ```

## Packaging with Briefcase

To create a standalone installer for distribution:

1. Install Briefcase:
   ```
   pip install briefcase
   ```

2. Create the application scaffold:
   ```
   briefcase create
   ```

3. Build the application:
   ```
   briefcase build
   ```

4. Package the application as an installer:
   ```
   briefcase package
   ```

The packaged installer will be available in the `dist` directory.

## License

This application is open-source and is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for details.

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
