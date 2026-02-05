const { contextBridge, ipcRenderer } = require('electron');

// Expose a safe, limited API to the renderer process
contextBridge.exposeInMainWorld('ariaElectron', {
  // System
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Node management
  getNodeStatus: () => ipcRenderer.invoke('get-node-status'),
  startNode: () => ipcRenderer.invoke('start-node'),
  stopNode: () => ipcRenderer.invoke('stop-node'),

  // Models
  getModels: () => ipcRenderer.invoke('get-models'),
  downloadModel: (name) => ipcRenderer.invoke('download-model', name),

  // Inference
  sendInference: (prompt, model, language) =>
    ipcRenderer.invoke('send-inference', { prompt, model, language }),

  // Backend status
  checkBackendStatus: () => ipcRenderer.invoke('check-backend-status'),

  // Events
  onNodeStatus: (callback) => {
    const handler = (_event, status) => callback(status);
    ipcRenderer.on('node-status', handler);
    return () => ipcRenderer.removeListener('node-status', handler);
  },

  // Platform info
  platform: process.platform,
});
