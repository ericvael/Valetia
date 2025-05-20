const aiAnalyzer = require('../services/aiAnalyzer');
const path = require('path');
const fs = require('fs');

exports.analyzeDocument = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'Aucun fichier fourni'
      });
    }
    
    const filePath = req.file.path;
    const analysis = await aiAnalyzer.analyzeDocument(filePath);
    
    res.status(200).json({
      success: true,
      analysis
    });
  } catch (error) {
    console.error('Erreur d\'analyse:', error);
    res.status(500).json({
      success: false,
      message: `Erreur lors de l'analyse: ${error.message}`
    });
  }
};
