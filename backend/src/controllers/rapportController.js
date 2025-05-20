const proofGenerator = require('../services/proofGenerator');

exports.generateReport = async (req, res) => {
  try {
    const data = req.body;
    
    if (!data.title) {
      return res.status(400).json({
        success: false,
        message: 'Le titre du rapport est requis'
      });
    }
    
    const result = await proofGenerator.generateReport(data);
    
    res.status(200).json({
      success: true,
      path: result.path,
      filename: result.filename
    });
  } catch (error) {
    console.error('Erreur de génération:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la génération du rapport',
      error: error.message
    });
  }
};

exports.getReports = (req, res) => {
  const fs = require('fs');
  const path = require('path');
  const outputDir = path.join(__dirname, '../../../output');
  
  fs.readdir(outputDir, (err, files) => {
    if (err) {
      return res.status(500).json({
        success: false,
        message: 'Erreur lors de la lecture des rapports',
        error: err.message
      });
    }
    
    const reports = files
      .filter(file => file.endsWith('.pdf'))
      .map(file => ({
        filename: file,
        path: path.join(outputDir, file)
      }));
    
    res.status(200).json({
      success: true,
      reports
    });
  });
};
