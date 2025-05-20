const proofGenerator = require('./proofGenerator');

const testData = {
  title: "Test de génération PDF",
  summary: "Ceci est un test du générateur de PDF pour le projet Valetia.",
  keyPoints: [
    "Point 1: Fonctionnalité de base",
    "Point 2: Formatage du document",
    "Point 3: Gestion des erreurs"
  ]
};

proofGenerator.generateReport(testData)
  .then(path => {
    console.log(`Rapport généré avec succès: ${path}`);
  })
  .catch(error => {
    console.error(`Erreur lors de la génération:`, error);
  });
