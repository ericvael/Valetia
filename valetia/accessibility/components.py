"""
Composants d'interface utilisateur accessibles pour ValetIA.

Ce module fournit des versions accessibles des composants d'interface 
Streamlit standard, avec un support amélioré pour les lecteurs d'écran.
"""

import streamlit as st
import html
from valetia.logger.loguru_adapter import loguru_logger as logger

def accessible_header(title, level=1, id=None, description=None):
    """
    Affiche un en-tête accessible avec description optionnelle pour les lecteurs d'écran.
    
    Args:
        title (str): Texte de l'en-tête
        level (int): Niveau de l'en-tête (1 à 6)
        id (str, optional): ID HTML pour l'en-tête
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    """
    # Valider le niveau
    if level < 1 or level > 6:
        level = 1
        logger.warning(f"Niveau d'en-tête invalide: {level}, utilisation du niveau 1")
    
    # Générer l'attribut id
    id_attr = f' id="{html.escape(id)}"' if id else ""
    
    # Générer la description pour les lecteurs d'écran
    sr_description = ""
    if description:
        sr_description = f'<span class="sr-only">{html.escape(description)}</span>'
    
    # Créer l'en-tête avec les attributs ARIA
    header_html = f"""
    <h{level}{id_attr} aria-label="{html.escape(title)}{', ' + html.escape(description) if description else ''}">
        {html.escape(title)}
        {sr_description}
    </h{level}>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def accessible_button(label, on_click=None, key=None, description=None, type="primary"):
    """
    Crée un bouton accessible avec description pour les lecteurs d'écran.
    
    Args:
        label (str): Texte du bouton
        on_click (callable, optional): Fonction à appeler au clic
        key (str, optional): Clé unique pour le bouton
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
        type (str, optional): Type de bouton ("primary" ou "secondary")
    
    Returns:
        bool: True si le bouton a été cliqué
    """
    # Créer un conteneur pour le bouton avec une description accessible
    if description:
        st.markdown(f'<div aria-hidden="true" class="sr-only">{html.escape(description)}</div>', unsafe_allow_html=True)
    
    # Afficher le bouton Streamlit standard
    return st.button(label, on_click=on_click, key=key, type=type)

def accessible_file_uploader(label, type=None, key=None, help=None, on_change=None, accept_multiple_files=False):
    """
    Crée un sélecteur de fichier accessible avec description améliorée.
    
    Args:
        label (str): Étiquette du sélecteur
        type (list, optional): Liste de types de fichiers acceptés
        key (str, optional): Clé unique
        help (str, optional): Texte d'aide
        on_change (callable, optional): Fonction appelée lors du changement
        accept_multiple_files (bool, optional): Accepter plusieurs fichiers
    
    Returns:
        file: Fichier(s) téléchargé(s)
    """
    # Améliorer le texte d'aide avec des informations d'accessibilité
    if help:
        enhanced_help = f"{help}\n\nNote d'accessibilité: Appuyez sur Espace pour ouvrir le sélecteur de fichier."
    else:
        enhanced_help = "Note d'accessibilité: Appuyez sur Espace pour ouvrir le sélecteur de fichier."
    
    # Créer un texte pour les lecteurs d'écran
    if type:
        type_str = ", ".join(type)
        sr_text = f"<div aria-live='polite' class='sr-only'>Sélecteur de fichier. Types acceptés: {type_str}</div>"
        st.markdown(sr_text, unsafe_allow_html=True)
    
    # Utiliser le uploader standard avec l'aide améliorée
    return st.file_uploader(
        label, 
        type=type, 
        key=key, 
        help=enhanced_help, 
        on_change=on_change,
        accept_multiple_files=accept_multiple_files
    )

def accessible_expander(title, expanded=False, description=None):
    """
    Crée un élément dépliable accessible avec description pour les lecteurs d'écran.
    
    Args:
        title (str): Titre de l'élément dépliable
        expanded (bool, optional): Si l'élément est déplié par défaut
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    
    Returns:
        expander: L'objet expander de Streamlit
    """
    # Créer une description améliorée
    if description:
        enhanced_title = f"{title} (Section dépliable: {description})"
    else:
        enhanced_title = f"{title} (Section dépliable)"
    
    # Créer un texte pour les lecteurs d'écran
    sr_text = f"""
    <div aria-live='polite' class='sr-only'>
        Section dépliable: {html.escape(title)}.
        {html.escape(description) if description else ''}
        {' Déjà déplié.' if expanded else ' Utiliser Entrée pour déplier ou replier.'}
    </div>
    """
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Créer l'expander standard
    return st.expander(title, expanded=expanded)

def accessible_tabs(tabs_list, descriptions=None):
    """
    Crée un groupe d'onglets accessible avec descriptions pour les lecteurs d'écran.
    
    Args:
        tabs_list (list): Liste des titres d'onglets
        descriptions (list, optional): Liste des descriptions pour chaque onglet
    
    Returns:
        tabs: L'objet tabs de Streamlit
    """
    # Préparer les descriptions
    if descriptions is None:
        descriptions = [""] * len(tabs_list)
    elif len(descriptions) != len(tabs_list):
        # Ajuster la taille de la liste de descriptions
        if len(descriptions) < len(tabs_list):
            descriptions.extend([""] * (len(tabs_list) - len(descriptions)))
        else:
            descriptions = descriptions[:len(tabs_list)]
    
    # Créer un texte pour les lecteurs d'écran
    sr_text = f"""
    <div aria-live='polite' class='sr-only'>
        Groupe d'onglets avec {len(tabs_list)} sections:
        {", ".join([f"{tabs_list[i]}{f' ({descriptions[i]})' if descriptions[i] else ''}" for i in range(len(tabs_list))])}
    </div>
    """
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Créer les onglets standard
    return st.tabs(tabs_list)

def accessible_text_input(label, value="", key=None, help=None, placeholder=None, on_change=None):
    """
    Crée un champ de saisie texte accessible avec description améliorée.
    
    Args:
        label (str): Étiquette du champ
        value (str, optional): Valeur initiale
        key (str, optional): Clé unique
        help (str, optional): Texte d'aide
        placeholder (str, optional): Texte d'exemple
        on_change (callable, optional): Fonction appelée lors du changement
    
    Returns:
        str: Texte saisi
    """
    # Améliorer le texte d'aide avec des informations d'accessibilité si nécessaire
    enhanced_help = help
    
    # Annoter pour les lecteurs d'écran si un placeholder existe
    if placeholder:
        sr_text = f"<div aria-live='polite' class='sr-only'>Champ de saisie: {label}. Exemple: {placeholder}</div>"
        st.markdown(sr_text, unsafe_allow_html=True)
    
    # Utiliser le input standard
    return st.text_input(
        label, 
        value=value, 
        key=key, 
        help=enhanced_help, 
        placeholder=placeholder,
        on_change=on_change
    )

def accessible_info(message, description=None):
    """
    Affiche un message d'information accessible avec description pour les lecteurs d'écran.
    
    Args:
        message (str): Texte du message
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    """
    # Préparer la description
    if description:
        sr_text = f"<div aria-live='polite' class='sr-only'>Information: {html.escape(message)}. {html.escape(description)}</div>"
    else:
        sr_text = f"<div aria-live='polite' class='sr-only'>Information: {html.escape(message)}</div>"
    
    # Ajouter l'élément pour lecteurs d'écran
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Afficher l'info standard
    st.info(message)

def accessible_success(message, description=None):
    """
    Affiche un message de succès accessible avec description pour les lecteurs d'écran.
    
    Args:
        message (str): Texte du message
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    """
    # Préparer la description
    if description:
        sr_text = f"<div aria-live='assertive' class='sr-only'>Succès: {html.escape(message)}. {html.escape(description)}</div>"
    else:
        sr_text = f"<div aria-live='assertive' class='sr-only'>Succès: {html.escape(message)}</div>"
    
    # Ajouter l'élément pour lecteurs d'écran
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Afficher le succès standard
    st.success(message)

def accessible_error(message, description=None):
    """
    Affiche un message d'erreur accessible avec description pour les lecteurs d'écran.
    
    Args:
        message (str): Texte du message d'erreur
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    """
    # Préparer la description
    if description:
        sr_text = f"<div aria-live='assertive' class='sr-only'>Erreur: {html.escape(message)}. {html.escape(description)}</div>"
    else:
        sr_text = f"<div aria-live='assertive' class='sr-only'>Erreur: {html.escape(message)}</div>"
    
    # Ajouter l'élément pour lecteurs d'écran
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Afficher l'erreur standard
    st.error(message)

def accessible_spinner(text, description=None):
    """
    Crée un indicateur de chargement accessible avec description pour les lecteurs d'écran.
    
    Args:
        text (str): Texte affiché pendant le chargement
        description (str, optional): Description supplémentaire pour les lecteurs d'écran
    
    Returns:
        spinner: L'objet spinner de Streamlit
    """
    # Préparer la description
    if description:
        sr_text = f"<div aria-live='polite' class='sr-only'>Chargement en cours: {html.escape(text)}. {html.escape(description)}</div>"
    else:
        sr_text = f"<div aria-live='polite' class='sr-only'>Chargement en cours: {html.escape(text)}</div>"
    
    # Ajouter l'élément pour lecteurs d'écran
    st.markdown(sr_text, unsafe_allow_html=True)
    
    # Créer le spinner standard
    return st.spinner(text)
