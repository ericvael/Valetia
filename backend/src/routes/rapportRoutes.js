const express = require('express');
const router = express.Router();
const rapportController = require('../controllers/rapportController');

router.post('/generate', rapportController.generateReport);
router.get('/', rapportController.getReports);

module.exports = router;
