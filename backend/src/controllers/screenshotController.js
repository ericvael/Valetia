const fs = require('fs');
const path = require('path');

exports.saveScreenshot = (req, res) => {
  const { imageData } = req.body;
  
  if (!imageData) {
    return res.status(400).json({ success: false, message: 'Données image manquantes' });
  }
  
  // Extraire la base64 et convertir en buffer
  const base64Data = imageData.replace(/^data:image\/png;base64,/, "");
  const buffer = Buffer.from(base64Data, 'base64');
  
  // Sauvegarder dans le dossier output
  const screenshotDir = path.join(__dirname, '../../../output/screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }
  
  const filename = `screenshot_${Date.now()}.png`;
  const filePath = path.join(screenshotDir, filename);
  
  fs.writeFile(filePath, buffer, (err) => {
    if (err) {
      return res.status(500).json({ success: false, message: err.message });
    }
    
    res.status(200).json({ 
      success: true, 
      message: 'Capture d\'écran sauvegardée',
      filename: filename,
      path: filePath
    });
  });
};
