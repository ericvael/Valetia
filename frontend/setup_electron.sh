#!/bin/bash

echo "🔧 Configuration de l'application Electron..."

# Créer le fichier main.js pour Electron
cat > electron.js << 'EOF'
const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'Valetia',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // En développement, charger le serveur Vite
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    // En production, charger les fichiers de build
    win.loadFile(path.join(__dirname, 'dist/index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
EOF

# Créer le fichier preload.js
cat > preload.js << 'EOF'
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
EOF

# Mettre à jour le package.json
cat > package.json << 'EOF'
{
  "name": "valetia",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "electron:dev": "NODE_ENV=development electron electron.js",
    "electron:build": "vite build && electron-builder"
  },
  "dependencies": {
    "html2canvas": "^1.4.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.55",
    "@types/react-dom": "^18.2.19",
    "@vitejs/plugin-react": "^4.2.1",
    "electron": "^29.0.1",
    "electron-builder": "^24.9.1",
    "vite": "^5.1.0"
  }
}
EOF

# Créer le fichier ScreenCapture modifié pour Electron
mkdir -p src/components/shared
cat > src/components/shared/ScreenCapture.jsx << 'EOF'
import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import './ScreenCapture.css';

const ScreenCapture = ({ targetRef, children }) => {
  const [imageData, setImageData] = useState(null);
  const [capturing, setCapturing] = useState(false);
  
  const captureScreen = async () => {
    if (!targetRef?.current) return;
    
    setCapturing(true);
    
    try {
      const canvas = await html2canvas(targetRef.current, {
        logging: false,
        useCORS: true,
        scale: 2
      });
      
      const image = canvas.toDataURL('image/png');
      setImageData(image);
    } catch (error) {
      console.error('Erreur lors de la capture:', error);
      alert(`Erreur lors de la capture: ${error.message}`);
    } finally {
      setCapturing(false);
    }
  };
  
  const downloadImage = async () => {
    if (!imageData) return;
    
    // Si nous sommes dans Electron
    if (window.electronAPI) {
      try {
        await window.electronAPI.saveFile(imageData, 'capture-valetia.png');
        alert('Capture d\'écran enregistrée avec succès !');
      } catch (error) {
        console.error('Erreur lors de l\'enregistrement:', error);
        alert(`Erreur lors de l'enregistrement: ${error.message}`);
      }
    } else {
      // Fallback pour le navigateur
      const link = document.createElement('a');
      link.href = imageData;
      link.download = 'capture-valetia.png';
      link.click();
    }
  };
  
  return (
    <div className="screen-capture-container">
      {children}
      
      <div className="screen-capture-controls">
        <button 
          onClick={captureScreen} 
          disabled={capturing}
          className="capture-button"
        >
          {capturing ? 'Capture en cours...' : 'Capturer l\'écran'}
        </button>
        
        {imageData && (
          <>
            <div className="screen-capture-preview">
              <img src={imageData} alt="Capture d'écran" />
            </div>
            <button 
              onClick={downloadImage} 
              className="download-button"
            >
              Enregistrer la capture
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ScreenCapture;
EOF

cat > src/components/shared/ScreenCapture.css << 'EOF'
.screen-capture-container {
  width: 100%;
  margin-bottom: 20px;
}

.screen-capture-controls {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.capture-button {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.capture-button:disabled {
  background-color: #cccccc;
}

.screen-capture-preview {
  margin-top: 10px;
  border: 1px solid #ddd;
  padding: 5px;
  max-height: 300px;
  overflow: auto;
}

.screen-capture-preview img {
  max-width: 100%;
}

.download-button {
  margin-top: 10px;
  background-color: #2196F3;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
EOF

echo "✅ Configuration Electron terminée!"
echo "📝 Pour lancer l'application, exécutez:"
echo "npm install"
echo "npm run dev (dans un terminal)"
echo "npm run electron:dev (dans un autre terminal)"
