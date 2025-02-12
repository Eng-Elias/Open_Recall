# FastAPI + React + Electron Desktop App

This project demonstrates integration of FastAPI backend with React frontend in a desktop application using Electron.js.

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

## Features
- Desktop application using Electron
- FastAPI backend
- React frontend with Bootstrap
- Hot-reloading enabled for development
- Integrated Python and Node.js processes

## Development
- The FastAPI server runs on `http://localhost:8000`
- Electron loads the FastAPI server URL in a desktop window
- Both processes are managed together using npm scripts
