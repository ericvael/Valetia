#!/bin/bash

# Créer les répertoires nécessaires
mkdir -p src/components/shared

# Créer le fichier ScreenCapture.jsx
cat > src/components/shared/ScreenCapture.jsx << 'EOF'
import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import { save } from '@tauri-apps/api/dialog';
import { writeBinaryFile } from '@tauri-apps/api/fs';
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
    
    try {
      // Utiliser le dialogue de fichier natif de Tauri
      const filePath = await save({
        filters: [{
          name: 'Images',
          extensions: ['png']
        }],
        defaultPath: 'capture-valetia.png'
      });
      
      if (filePath) {
        // Convertir la data URL en blob
        const base64Data = imageData.replace(/^data:image\/png;base64,/, '');
        const binaryData = atob(base64Data);
        const byteArray = new Uint8Array(binaryData.length);
        
        for (let i = 0; i < binaryData.length; i++) {
          byteArray[i] = binaryData.charCodeAt(i);
        }
        
        // Écrire le fichier sur le disque
        await writeBinaryFile(filePath, byteArray);
        alert('Capture d\'écran enregistrée avec succès !');
      }
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement:', error);
      alert(`Erreur lors de l'enregistrement: ${error.message}`);
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

# Créer le fichier ScreenCapture.css
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

# Créer le fichier App.jsx
cat > src/App.jsx << 'EOF'
import { useRef } from 'react'
import './App.css'
import ScreenCapture from './components/shared/ScreenCapture'

function App() {
  const contentRef = useRef(null);

  return (
    <div className="app-container">
      <h1>Valetia</h1>
      
      <ScreenCapture targetRef={contentRef}>
        <div className="content-area" ref={contentRef}>
          <h2>Zone de test à capturer</h2>
          <p>Cette zone sera capturée lorsque vous cliquerez sur le bouton ci-dessous.</p>
          
          <div className="test-card">
            <h3>Exemple de dossier</h3>
            <ul>
              <li><strong>Projet:</strong> Valetia</li>
              <li><strong>Date:</strong> 19 mai 2025</li>
              <li><strong>Statut:</strong> En développement</li>
            </ul>
          </div>
        </div>
      </ScreenCapture>
    </div>
  )
}

export default App
EOF

# Créer le fichier App.css
cat > src/App.css << 'EOF'
#root {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.content-area {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 20px;
  background-color: white;
  text-align: left;
  width: 100%;
  box-sizing: border-box;
}

.test-card {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 15px;
  margin-top: 15px;
}

.test-card h3 {
  margin-top: 0;
  color: #495057;
}

.test-card ul {
  list-style-type: none;
  padding-left: 0;
}

.test-card li {
  margin-bottom: 8px;
}
EOF

echo "Tous les fichiers ont été créés avec succès !"
