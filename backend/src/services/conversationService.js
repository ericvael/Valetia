const natural = require('natural');
const fs = require('fs');
const path = require('path');

class ConversationService {
  constructor() {
    this.memory = [];
    this.legalKeywords = {
      'prudhommes': ['licenciement', 'contrat', 'travail', 'salarié', 'employeur', 'préavis', 'indemnité'],
      'copropriete': ['assemblée', 'syndic', 'charges', 'copropriétaire', 'immeuble', 'règlement']
    };
    
    // Réponses prédéfinies par catégorie
    this.responses = {
      'prudhommes': {
        'default': "Je peux vous aider avec votre dossier prud'hommal. Pourriez-vous me donner plus de détails?",
        'licenciement': "Pour un licenciement, il est important de vérifier la procédure suivie et les motifs invoqués. Avez-vous reçu une lettre de licenciement?",
        'contrat': "Les détails de votre contrat de travail sont essentiels. S'agit-il d'un CDI, CDD ou autre type de contrat?",
        'indemnité': "Pour les indemnités, nous devons examiner votre ancienneté et les circonstances de la rupture du contrat."
      },
      'copropriete': {
        'default': "Je peux vous aider avec votre dossier de copropriété. Quelle est la nature du problème?",
        'charges': "Pour contester des charges, il faut vérifier leur répartition selon le règlement de copropriété. Avez-vous accès à ce document?",
        'syndic': "Pour un litige avec le syndic, nous devons examiner ses obligations légales et contractuelles. Quelle est la nature du différend?",
        'travaux': "Concernant les travaux en copropriété, la décision doit être prise en assemblée générale. Avez-vous le procès-verbal?"
      },
      'général': {
        'default': "Bienvenue sur Valetia. Je peux vous aider avec vos questions juridiques concernant les prud'hommes ou la copropriété. Quelle est votre question?",
        'bonjour': "Bonjour! Comment puis-je vous aider aujourd'hui?",
        'merci': "Je vous en prie. N'hésitez pas si vous avez d'autres questions.",
        'aide': "Je peux vous aider à analyser des documents, générer des rapports ou répondre à vos questions juridiques."
      }
    };
  }

  process(message) {
    // Garder l'historique limité
    this.memory.push(message);
    if (this.memory.length > 5) this.memory.shift();
    
    // Déterminer la catégorie
    const category = this._identifyCategory(message);
    
    // Trouver les mots-clés pertinents
    const keywords = this._extractKeywords(message, category);
    
    // Générer la réponse
    return this._generateResponse(message, category, keywords);
  }
  
  _identifyCategory(message) {
    let maxScore = 0;
    let category = 'général';
    
    for (const [cat, keywords] of Object.entries(this.legalKeywords)) {
      let score = 0;
      for (const keyword of keywords) {
        if (message.toLowerCase().includes(keyword)) {
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
  
  _extractKeywords(message, category) {
    const keywords = [];
    const text = message.toLowerCase();
    
    // Chercher les mots-clés de la catégorie
    if (category !== 'général' && this.legalKeywords[category]) {
      for (const keyword of this.legalKeywords[category]) {
        if (text.includes(keyword)) {
          keywords.push(keyword);
        }
      }
    }
    
    // Mots-clés généraux
    const generalKeywords = ['bonjour', 'merci', 'aide'];
    for (const keyword of generalKeywords) {
      if (text.includes(keyword)) {
        keywords.push(keyword);
      }
    }
    
    return keywords;
  }
  
  _generateResponse(message, category, keywords) {
    // Sélectionner une réponse basée sur les mots-clés
    let response = '';
    
    if (keywords.length > 0) {
      // Utiliser le premier mot-clé trouvé
      const keyword = keywords[0];
      
      if (this.responses[category] && this.responses[category][keyword]) {
        response = this.responses[category][keyword];
      } else if (this.responses['général'][keyword]) {
        response = this.responses['général'][keyword];
      } else {
        response = this.responses[category]['default'] || this.responses['général']['default'];
      }
    } else {
      response = this.responses[category]['default'] || this.responses['général']['default'];
    }
    
    return {
      message: response,
      category: category
    };
  }
}

module.exports = new ConversationService();
