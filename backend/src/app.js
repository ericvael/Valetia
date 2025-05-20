const express = require('express');
const path = require('path');
const multer = require('multer');
const app = express();
const port = 3000;

// Middleware
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../../frontend/public')));

// Routes
app.use('/api/rapports', require('./routes/rapportRoutes'));
app.use('/api/screenshots', require('./routes/screenshotRoutes'));
app.use('/api/documents', require('./routes/documentRoutes'));
app.use('/api/conversation', require('./routes/conversationRoutes'));

// Route pour télécharger les PDF
app.get('/download/:filename', (req, res) => {
  const file = path.join(__dirname, '../../output', req.params.filename);
  res.download(file);
});

// Route principale
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../../frontend/public/index.html'));
});

// Démarrage du serveur
app.listen(port, () => {
  console.log(`Valetia est en cours d'exécution sur http://localhost:${port}`);
});
