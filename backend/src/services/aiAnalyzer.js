const pdfParse = require('pdf-parse');
const natural = require('natural');
const fs = require('fs');
const path = require('path');

class AIAnalyzer {
  async analyzeDocument(filePath) {
    try {
      const extension = path.extname(filePath).toLowerCase();
      let text = '';
      
      // Extraction du texte selon le type de fichier
      if (extension === '.pdf') {
        const dataBuffer = fs.readFileSync(filePath);
        const data = await pdfParse(dataBuffer);
        text = data.text;
      } else if (extension === '.txt') {
        text = fs.readFileSync(filePath, 'utf8');
      } else {
        throw new Error(`Format de fichier non supporté: ${extension}`);
      }
      
      // Analyse du contenu
      const analysis = {
        category: this._classifyDocument(text),
        dates: this._extractDates(text),
        amounts: this._extractAmounts(text),
        keyPoints: this._extractKeyPoints(text),
      };
      
      return analysis;
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      throw error;
    }
  }
  
  // Classification du document
  _classifyDocument(text) {
    const categories = {
      'prudhommes': ['licenciement', 'contrat', 'travail', 'salarié', 'employeur', 'préavis', 'indemnité'],
      'copropriete': ['assemblée', 'syndic', 'charges', 'copropriétaire', 'immeuble', 'règlement']
    };
    
    let maxScore = 0;
    let category = 'indéterminé';
    
    for (const [cat, keywords] of Object.entries(categories)) {
      let score = 0;
      for (const keyword of keywords) {
        if (text.toLowerCase().includes(keyword)) {
          score++;
        }
      }
      
      if (score > maxScore) {
        maxScore = score;
        category = cat;
      }
    }
    
    return category;
  }
  
  // Extraction des dates
  _extractDates(text) {
    const dateRegex = /(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2,4})/g;
    const matches = [...text.matchAll(dateRegex)];
    return matches.map(match => match[0]);
  }
  
  // Extraction des montants
  _extractAmounts(text) {
    const amountRegex = /(\d+(?:\s*\d+)*(?:[,.]\d+)?)(?:\s*€|\s*euros)/gi;
    const matches = [...text.matchAll(amountRegex)];
    return matches.map(match => match[0].trim());
  }
  
  // Extraction des points clés
  _extractKeyPoints(text) {
    const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 10);
    const keyPoints = [];
    
    // Recherche des phrases avec des mots-clés importants
    const allKeywords = [
      'licenciement', 'contrat', 'travail', 'salarié', 'employeur', 'préavis', 'indemnité',
      'assemblée', 'syndic', 'charges', 'copropriétaire', 'immeuble', 'règlement'
    ];
    
    for (const sentence of sentences) {
      const hasKeyword = allKeywords.some(keyword => sentence.toLowerCase().includes(keyword));
      
      if (hasKeyword && keyPoints.length < 5) {
        keyPoints.push(sentence);
      }
    }
    
    return keyPoints;
  }
}

module.exports = new AIAnalyzer();
