const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// Désactiver le sandbox pour le développement
app.commandLine.appendSwitch('no-sandbox');

// Gardez une référence globale de l'objet window
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'Valetia',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // En développement, chargez le serveur de dev Vite
  mainWindow.loadURL('http://localhost:5174');
  
  // Décommentez pour ouvrir les outils de développement
  // mainWindow.webContents.openDevTools();

  mainWindow.on('closed', function () {
    mainWindow = null;
  });

  // Gestion de sauvegarde d'images
  ipcMain.handle('save-image', async (event, dataUrl, defaultPath) => {
    try {
      const { canceled, filePath } = await dialog.showSaveDialog({
        title: 'Enregistrer la capture d\'écran',
        defaultPath: defaultPath || 'capture.png',
        filters: [{ name: 'Images', extensions: ['png'] }]
      });

      if (canceled || !filePath) {
        return { success: false, message: 'Opération annulée' };
      }

      // Convertir data URL en buffer
      const base64Data = dataUrl.replace(/^data:image\/png;base64,/, '');
      const buffer = Buffer.from(base64Data, 'base64');

      // Écrire le fichier
      fs.writeFileSync(filePath, buffer);
      
      return { success: true, filePath };
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      return { success: false, message: error.message };
    }
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', function () {
  if (mainWindow === null) createWindow();
});
