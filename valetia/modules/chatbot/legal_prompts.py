"""
Module contenant des templates de prompts spécialisés pour le domaine juridique français.
"""

# Template pour injecter l'expertise juridique dans les réponses
LEGAL_EXPERTISE_TEMPLATE = """
Tu es Valetia, un assistant juridique français spécialisé en droit de la copropriété, droit du travail (prud'hommes) et droit des successions. Tu dois répondre aux questions en français, de manière précise mais compréhensible pour des non-juristes.

Ton expertise couvre notamment :
- Le droit de la copropriété (loi du 10 juillet 1965, décrets, jurisprudence récente)
- Le droit du travail et procédures prud'homales (Code du travail, conventions collectives, procédures)
- Le droit des successions (Code civil, règles fiscales, procédures notariales)
- Les principes généraux du droit français et européen pertinents

Lorsque tu réponds :
1. Identifie d'abord la question juridique posée
2. Donne une réponse vulgarisée claire
3. Si nécessaire, cite brièvement les textes de loi pertinents
4. Propose des pistes d'action concrètes
5. Rappelle que tes conseils sont informatifs et ne remplacent pas l'avis d'un professionnel du droit

Question : {question}

Réponse juridique vulgarisée :
"""

# Template pour la vulgarisation juridique
SIMPLIFICATION_TEMPLATE = """
Explique la notion juridique suivante en termes simples, comme si tu t'adressais à quelqu'un qui n'a aucune connaissance en droit :

{concept}

Explication vulgarisée :
"""

# Formulations pour les réponses juridiques
LEGAL_PREFIXES = [
    "D'un point de vue juridique, ",
    "Selon la législation française, ",
    "Dans le cadre légal actuel, ",
    "Au regard du droit français, ",
    "D'après la réglementation en vigueur, "
]

# Modèles de fin de réponse
LEGAL_DISCLAIMERS = [
    "Notez que cette information est donnée à titre indicatif et ne constitue pas un conseil juridique personnalisé.",
    "Il est recommandé de consulter un professionnel du droit pour votre situation spécifique.",
    "Cette réponse se base sur les textes en vigueur, mais l'interprétation peut varier selon les juridictions.",
    "Pour une analyse complète de votre situation, consultez un avocat spécialisé.",
    "Ces informations générales devraient être adaptées à votre cas particulier avec l'aide d'un professionnel."
]

# Liste de textes juridiques français fréquemment cités
COMMON_LEGAL_REFERENCES = {
    "copropriété": [
        "la loi du 10 juillet 1965 fixant le statut de la copropriété",
        "le décret du 17 mars 1967 d'application de la loi sur la copropriété",
        "l'article 14 de la loi de 1965 relatif aux pouvoirs du syndicat des copropriétaires",
        "l'article 18 de la loi de 1965 sur les missions du syndic"
    ],
    "prud'hommes": [
        "l'article L.1411-1 du Code du travail définissant la compétence des Conseils de prud'hommes",
        "l'article L.1235-3 du Code du travail concernant les indemnités de licenciement sans cause réelle et sérieuse",
        "le barème Macron (articles L.1235-3 et suivants du Code du travail)",
        "l'article L.1221-1 du Code du travail sur le contrat de travail"
    ],
    "succession": [
        "l'article 756 du Code civil sur les ordres de succession",
        "l'article 913 du Code civil relatif à la réserve héréditaire",
        "l'article 1094-1 du Code civil sur les donations entre époux",
        "l'article 804 du Code civil concernant l'acceptation sous bénéfice d'inventaire"
    ]
}

def get_legal_prompt(question: str) -> str:
    """
    Génère un prompt juridique adapté à la question posée.
    
    Args:
        question: La question de l'utilisateur
        
    Returns:
        Le prompt enrichi de contexte juridique
    """
    return LEGAL_EXPERTISE_TEMPLATE.format(question=question)

def get_vulgarization_prompt(concept: str) -> str:
    """
    Génère un prompt pour vulgariser un concept juridique.
    
    Args:
        concept: Le concept juridique à vulgariser
        
    Returns:
        Le prompt pour la vulgarisation
    """
    return SIMPLIFICATION_TEMPLATE.format(concept=concept)
