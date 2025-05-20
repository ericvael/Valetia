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
