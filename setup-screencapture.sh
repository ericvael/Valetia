#!/bin/bash

# Création des dossiers nécessaires
mkdir -p src/components/shared
mkdir -p src/components/ui
mkdir -p src/lib

# Création du composant ScreenCapture.jsx
cat > src/components/shared/ScreenCapture.jsx << 'EOL'
import React, { useState, useCallback } from 'react';
import html2canvas from 'html2canvas';

const ScreenCapture = ({ targetRef, onCapture }) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  const captureScreen = useCallback(() => {
    if (!targetRef.current) return;
    
    setIsCapturing(true);
    
    html2canvas(targetRef.current, {
      logging: false,
      useCORS: true,
      scale: 2
    }).then(canvas => {
      const image = canvas.toDataURL('image/png');
      setCapturedImage(image);
      setIsDialogOpen(true);
      setIsCapturing(false);
      
      if (onCapture) {
        onCapture(image);
      }
    }).catch(err => {
      console.error('Capture failed:', err);
      setIsCapturing(false);
    });
  }, [targetRef, onCapture]);
  
  const downloadImage = useCallback(() => {
    if (!capturedImage) return;
    
    const link = document.createElement('a');
    link.href = capturedImage;
    link.download = `valetia-capture-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
    link.click();
  }, [capturedImage]);
  
  const copyToClipboard = useCallback(async () => {
    if (!capturedImage) return;
    
    try {
      const blob = await fetch(capturedImage).then(res => res.blob());
      await navigator.clipboard.write([
        new ClipboardItem({
          [blob.type]: blob
        })
      ]);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [capturedImage]);
  
  return (
    <>
      <button 
        onClick={captureScreen} 
        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 border rounded-md flex items-center gap-2"
        disabled={isCapturing}
      >
        {isCapturing ? 'Capture en cours...' : 'Capturer'}
      </button>
      
      {isDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-lg w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Capture d'écran</h3>
              <button 
                onClick={() => setIsDialogOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="border rounded-md overflow-hidden mb-4">
              {capturedImage && (
                <img src={capturedImage} alt="Capture d'écran" className="w-full" />
              )}
            </div>
            
            <div className="flex justify-between">
              <button 
                onClick={() => setIsDialogOpen(false)}
                className="px-3 py-1 border rounded-md"
              >
                Fermer
              </button>
              <div className="space-x-2">
                <button 
                  onClick={copyToClipboard}
                  className="px-3 py-1 border rounded-md"
                >
                  Copier
                </button>
                <button 
                  onClick={downloadImage}
                  className="px-3 py-1 bg-blue-500 text-white rounded-md"
                >
                  Télécharger
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ScreenCapture;
EOL

# Créer une page de test simple
cat > src/App.jsx << 'EOL'
import React, { useRef } from 'react';
import ScreenCapture from './components/shared/ScreenCapture';

function App() {
  const contentRef = useRef(null);
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Valetia - Capture d'écran</h1>
        <ScreenCapture targetRef={contentRef} />
      </div>
      
      <div ref={contentRef} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: 'white' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '10px' }}>Zone de capture d'écran</h2>
        <p style={{ marginBottom: '15px' }}>Cette zone sera capturée lorsque vous cliquerez sur le bouton "Capturer".</p>
        
        <div style={{ backgroundColor: '#f0f7ff', padding: '15px', borderRadius: '6px', border: '1px solid #d0e3ff' }}>
          <h3 style={{ color: '#1e40af', marginBottom: '10px', fontWeight: '500' }}>Exemple de document juridique</h3>
          <p>Ce composant permet de faire une capture d'écran de n'importe quelle partie de l'interface pour l'inclure dans vos rapports juridiques.</p>
          <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
            <li>Capture d'irrégularités dans les documents</li>
            <li>Sauvegarde de preuves visuelles</li>
            <li>Intégration dans les rapports</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
EOL

# Créer un fichier main.jsx minimal
cat > src/main.jsx << 'EOL'
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOL

# Créer un fichier HTML minimal
cat > index.html << 'EOL'
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Valetia - Capture d'écran</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
EOL

# Mettre à jour package.json avec les scripts nécessaires
cat > package.json << 'EOL'
{
  "name": "valetia-screencapture",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "html2canvas": "^1.4.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
EOL

# Créer une configuration Vite minimale
cat > vite.config.js << 'EOL'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()]
});
EOL

echo "Configuration terminée. Exécutez maintenant:"
echo "npm install && npm run dev"
