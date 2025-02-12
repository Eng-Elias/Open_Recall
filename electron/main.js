const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    // Wait for FastAPI server to start
    setTimeout(() => {
        mainWindow.loadURL('http://localhost:8000');
    }, 3000);

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startPythonServer() {
    // Start FastAPI server
    const pythonPath = 'python';
    pythonProcess = spawn(pythonPath, ['main.py'], {
        cwd: path.join(__dirname, '..')
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
    });
}

app.on('ready', () => {
    startPythonServer();
    createWindow();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        // Kill Python process when app closes
        if (pythonProcess) {
            pythonProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});
