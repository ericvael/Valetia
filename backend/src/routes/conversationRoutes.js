const express = require('express');
const router = express.Router();
const conversationController = require('../controllers/conversationController');

router.post('/message', conversationController.processMessage);

module.exports = router;
