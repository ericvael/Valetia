import React from 'react';
import html2canvas from 'html2canvas';
function ScreenCapture() {
    const handleCapture = () => {
  html2canvas(document.body).then(canvas => {
    const link = document.createElement('a');
    link.download = 'capture.png';
    link.href = canvas.toDataURL();
    link.click();
  });
};
  return (
    <div>
      <h1>Composant de capture d'écran</h1>
      <button onClick={handleCapture}>Capturer l'écran</button>
    </div>
  );
}

export default ScreenCapture;