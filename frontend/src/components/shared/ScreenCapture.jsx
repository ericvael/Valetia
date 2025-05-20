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
