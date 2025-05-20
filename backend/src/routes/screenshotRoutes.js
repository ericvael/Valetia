const express = require('express');
const router = express.Router();
const screenshotController = require('../controllers/screenshotController');

router.post('/save', screenshotController.saveScreenshot);

module.exports = router;
