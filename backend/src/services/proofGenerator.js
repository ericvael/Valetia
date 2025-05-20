const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');

class ProofGenerator {
  constructor() {
    this.outputDir = path.join(__dirname, '../../../output');
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  generateReport(data) {
    return new Promise((resolve, reject) => {
      try {
        const filename = `rapport_${Date.now()}.pdf`;
        const outputPath = path.join(this.outputDir, filename);
        
        const doc = new PDFDocument();
        const stream = fs.createWriteStream(outputPath);
        
        doc.pipe(stream);
        
        // Titre
        doc.fontSize(24).text('Rapport Valetia', { align: 'center' });
        doc.moveDown();
        
        // Informations
        doc.fontSize(14).text(`Dossier: ${data.title || 'Sans titre'}`);
        doc.fontSize(12).text(`Date: ${new Date().toLocaleDateString('fr-FR')}`);
        doc.moveDown();
        
        // Contenu
        doc.fontSize(16).text('Résumé');
        doc.fontSize(12).text(data.summary || 'Aucun résumé disponible');
        doc.moveDown();
        
        // Points clés
        if (data.keyPoints && data.keyPoints.length > 0) {
          doc.fontSize(16).text('Points clés');
          data.keyPoints.forEach((point, i) => {
            doc.fontSize(12).text(`${i+1}. ${point}`);
          });
        }
        
        doc.end();
        
        stream.on('finish', () => {
          resolve({
            path: outputPath,
            filename: filename
          });
        });
        
      } catch (error) {
        reject(error);
      }
    });
  }
}

module.exports = new ProofGenerator();
