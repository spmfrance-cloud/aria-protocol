const { app, BrowserWindow, ipcMain, shell, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Disable GPU acceleration for compatibility
app.disableHardwareAcceleration();

let mainWindow = null;
let tray = null;
let ariaProcess = null;

const ARIA_API_BASE = 'http://127.0.0.1:3000';

// ── Window Management ──────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'ARIA Desktop',
    icon: path.join(__dirname, '..', 'src-tauri', 'icons', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
    backgroundColor: '#0a0a0f',
    show: false,
  });

  // Load the frontend
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Open external links in the default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ── System Tray ────────────────────────────────────────────────────

function createTray() {
  const iconPath = path.join(__dirname, '..', 'src-tauri', 'icons', '32x32.png');
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show ARIA Desktop',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      },
    },
  ]);

  tray.setToolTip('ARIA Desktop');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// ── ARIA Node Management ───────────────────────────────────────────

function startAriaNode() {
  return new Promise((resolve, reject) => {
    if (ariaProcess) {
      reject(new Error('Node is already running'));
      return;
    }

    try {
      ariaProcess = spawn('aria', ['node', 'start', '--port', '8765', '--api-port', '3000'], {
        stdio: 'pipe',
      });

      ariaProcess.on('error', (err) => {
        ariaProcess = null;
        reject(new Error(`Failed to start node: ${err.message}`));
      });

      ariaProcess.on('exit', (code) => {
        ariaProcess = null;
        if (mainWindow) {
          mainWindow.webContents.send('node-status', { running: false, code });
        }
      });

      // Give the node a moment to start
      setTimeout(() => resolve('Node started successfully'), 1000);
    } catch (err) {
      reject(err);
    }
  });
}

function stopAriaNode() {
  return new Promise((resolve) => {
    if (!ariaProcess) {
      resolve('Node is not running');
      return;
    }

    ariaProcess.kill('SIGTERM');
    ariaProcess = null;
    resolve('Node stopped');
  });
}

// ── IPC Handlers ───────────────────────────────────────────────────

function setupIPC() {
  ipcMain.handle('get-system-info', () => ({
    os: process.platform,
    arch: process.arch,
    version: app.getVersion(),
  }));

  ipcMain.handle('get-app-version', () => app.getVersion());

  ipcMain.handle('get-node-status', async () => {
    const running = ariaProcess !== null;
    try {
      const response = await fetch(`${ARIA_API_BASE}/v1/status`);
      const data = await response.json();
      return { ...data, running: true };
    } catch {
      return {
        running,
        peer_count: 0,
        uptime_seconds: 0,
        version: app.getVersion(),
        backend: running ? 'offline' : 'none',
        model: null,
      };
    }
  });

  ipcMain.handle('start-node', async () => {
    return startAriaNode();
  });

  ipcMain.handle('stop-node', async () => {
    return stopAriaNode();
  });

  ipcMain.handle('get-models', async () => {
    try {
      const response = await fetch(`${ARIA_API_BASE}/v1/models`);
      return await response.json();
    } catch {
      return [
        { name: 'BitNet-b1.58-large', params: '0.7B', size: '400 MB', downloaded: false, description: 'Fast, lightweight model' },
        { name: 'BitNet-b1.58-2B-4T', params: '2.4B', size: '1.3 GB', downloaded: false, description: 'Best balance of speed and quality' },
        { name: 'Llama3-8B-1.58', params: '8.0B', size: '4.2 GB', downloaded: false, description: 'Most capable model' },
      ];
    }
  });

  ipcMain.handle('download-model', async (_event, name) => {
    try {
      const response = await fetch(`${ARIA_API_BASE}/v1/models/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      return await response.json();
    } catch (err) {
      throw new Error(`Failed to start download: ${err.message}`);
    }
  });

  ipcMain.handle('send-inference', async (_event, { prompt, model }) => {
    try {
      const response = await fetch(`${ARIA_API_BASE}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          messages: [{ role: 'user', content: prompt }],
          stream: false,
        }),
      });
      const data = await response.json();
      return {
        text: data.choices?.[0]?.message?.content || 'No response',
        tokens_per_second: data.usage?.tokens_per_second || 0,
        model,
        energy_mj: data.usage?.energy_mj || 0,
      };
    } catch (err) {
      throw new Error(`Inference request failed: ${err.message}`);
    }
  });
}

// ── App Lifecycle ──────────────────────────────────────────────────

app.whenReady().then(() => {
  setupIPC();
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // On macOS, keep the app running in the tray
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', async () => {
  // Clean up the ARIA node process
  if (ariaProcess) {
    ariaProcess.kill('SIGTERM');
    ariaProcess = null;
  }
});
