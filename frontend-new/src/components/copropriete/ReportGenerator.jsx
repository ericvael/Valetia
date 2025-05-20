import React, { useState } from 'react';
import { jsPDF } from 'jspdf';
import './ReportGenerator.css';

const ReportGenerator = () => {
  const [title, setTitle] = useState('');
  const [events, setEvents] = useState([{ date: '', description: '' }]);
  const [generating, setGenerating] = useState(false);

  const addEvent = () => {
    setEvents([...events, { date: '', description: '' }]);
  };

  const updateEvent = (index, field, value) => {
    const updatedEvents = [...events];
    updatedEvents[index][field] = value;
    setEvents(updatedEvents);
  };

  const removeEvent = (index) => {
    const updatedEvents = [...events];
    updatedEvents.splice(index, 1);
    setEvents(updatedEvents);
  };

  const generateReport = () => {
    setGenerating(true);
    
    try {
      const doc = new jsPDF();
      
      // En-tête
      doc.setFontSize(22);
      doc.text('Dossier Copropriété', 105, 20, { align: 'center' });
      
      // Titre
      doc.setFontSize(16);
      doc.text(title || 'Chronologie des événements', 105, 30, { align: 'center' });
      
      // Date de génération
      doc.setFontSize(10);
      doc.text(`Généré le ${new Date().toLocaleDateString()}`, 105, 40, { align: 'center' });
      
      // Chronologie
      doc.setFontSize(12);
      doc.text('Chronologie:', 20, 50);
      
      let y = 60;
      
      events
        .sort((a, b) => new Date(a.date) - new Date(b.date))
        .forEach((event, index) => {
          if (event.date && event.description) {
            doc.setFont(undefined, 'bold');
            doc.text(`${new Date(event.date).toLocaleDateString()}:`, 20, y);
            doc.setFont(undefined, 'normal');
            
            // Gestion des textes longs avec retour à la ligne
            const splitText = doc.splitTextToSize(event.description, 150);
            doc.text(splitText, 50, y);
            
            y += 10 * (splitText.length);
            
            // Ajouter une nouvelle page si nécessaire
            if (y > 280) {
              doc.addPage();
              y = 20;
            }
          }
        });
      
      // Pied de page
      doc.setFontSize(10);
      const pageCount = doc.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.text(`Page ${i} sur ${pageCount}`, 105, 290, { align: 'center' });
        doc.text('Document généré par Valetia - Confidentiel', 105, 295, { align: 'center' });
      }
      
      // Enregistrer le PDF
      doc.save('rapport-copropriete.pdf');
      
      alert('Rapport généré avec succès !');
    } catch (error) {
      console.error('Erreur lors de la génération du rapport:', error);
      alert(`Erreur lors de la génération du rapport: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="report-generator">
      <h2>Générateur de rapport copropriété</h2>
      
      <div className="form-group">
        <label htmlFor="title">Titre du rapport:</label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Ex: Chronologie des dysfonctionnements du syndic"
        />
      </div>
      
      <h3>Chronologie des événements</h3>
      
      {events.map((event, index) => (
        <div key={index} className="event-row">
          <div className="form-group">
            <label htmlFor={`date-${index}`}>Date:</label>
            <input
              type="date"
              id={`date-${index}`}
              value={event.date}
              onChange={(e) => updateEvent(index, 'date', e.target.value)}
            />
          </div>
          
          <div className="form-group description">
            <label htmlFor={`description-${index}`}>Description:</label>
            <textarea
              id={`description-${index}`}
              value={event.description}
              onChange={(e) => updateEvent(index, 'description', e.target.value)}
              placeholder="Description de l'événement"
              rows="2"
            />
          </div>
          
          <button
            type="button"
            className="remove-button"
            onClick={() => removeEvent(index)}
            disabled={events.length === 1}
          >
            Supprimer
          </button>
        </div>
      ))}
      
      <div className="button-group">
        <button type="button" className="add-button" onClick={addEvent}>
          Ajouter un événement
        </button>
        
        <button
          type="button"
          className="generate-button"
          onClick={generateReport}
          disabled={generating || !events.some(e => e.date && e.description)}
        >
          {generating ? 'Génération en cours...' : 'Générer le rapport PDF'}
        </button>
      </div>
    </div>
  );
};

export default ReportGenerator;
