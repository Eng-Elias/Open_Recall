# Open_Recall

## Overview

Open_Recall is a powerful desktop application that helps you search, find and analyze anything you've seen on your PC. Using advanced search capabilities, you can easily locate past activities, documents, applications, and websites based on your memory fragments or timeline navigation.

## Project Structure

```
.
├── electron/          # Electron main process
│   └── main.js       # Electron entry point
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
├── package.json     # Node.js dependencies
├── static/          # Static files
│   └── js/
│       └── App.js   # React components
└── templates/
    └── index.html   # Main template
```

## Setup and Running

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install Node.js dependencies:

```bash
npm install
```

3. Run the desktop application (this will start both FastAPI and Electron):

```bash
npm run dev
```

## License

This application is open-source and is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for details.

Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
