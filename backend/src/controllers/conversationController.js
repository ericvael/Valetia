const conversationService = require('../services/conversationService');

exports.processMessage = (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({
        success: false,
        message: 'Le message est requis'
      });
    }
    
    const response = conversationService.process(message);
    
    res.status(200).json({
      success: true,
      response: response
    });
  } catch (error) {
    console.error('Erreur de conversation:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors du traitement du message',
      error: error.message
    });
  }
};
