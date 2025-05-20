import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import './ScreenCapture.css';

const ScreenCapture = ({ targetRef, children }) => {
  const [imageData, setImageData] = useState(null);
  const [capturing, setCapturing] = useState(false);
  
  const captureScreen = async () => {
    if (!targetRef?.current) {
      alert("Aucun élément à capturer");
      return;
    }
    
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
  
  const downloadImage = () => {
    if (!imageData) return;
    
    // Méthode simple pour télécharger dans le navigateur
    const link = document.createElement('a');
    link.href = imageData;
    link.download = 'capture-valetia.png';
    link.click();
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
              Télécharger la capture
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ScreenCapture;
