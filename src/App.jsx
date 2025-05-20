import React, { useRef } from 'react';
import ScreenCapture from './components/shared/ScreenCapture';

function App() {
  const contentRef = useRef(null);
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Valetia - Capture d'écran</h1>
        <ScreenCapture targetRef={contentRef} />
      </div>
      
      <div ref={contentRef} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: 'white' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '10px' }}>Zone de capture d'écran</h2>
        <p style={{ marginBottom: '15px' }}>Cette zone sera capturée lorsque vous cliquerez sur le bouton "Capturer".</p>
        
        <div style={{ backgroundColor: '#f0f7ff', padding: '15px', borderRadius: '6px', border: '1px solid #d0e3ff' }}>
          <h3 style={{ color: '#1e40af', marginBottom: '10px', fontWeight: '500' }}>Exemple de document juridique</h3>
          <p>Ce composant permet de faire une capture d'écran de n'importe quelle partie de l'interface pour l'inclure dans vos rapports juridiques.</p>
          <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
            <li>Capture d'irrégularités dans les documents</li>
            <li>Sauvegarde de preuves visuelles</li>
            <li>Intégration dans les rapports</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
