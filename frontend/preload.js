window.addEventListener('DOMContentLoaded', () => {
  const { ipcRenderer } = require('electron');

  // Exposer les fonctions Electron au frontend
  window.electronAPI = {
    saveFile: async (data, defaultPath) => {
      const result = await ipcRenderer.invoke('save-file', data, defaultPath);
      return result;
    }
  };
});
