import { useRef } from 'react'
import './App.css'
import ScreenCapture from './components/shared/ScreenCapture'

function App() {
  const contentRef = useRef(null);

  return (
    <div className="app-container">
      <h1>Valetia</h1>
      
      <ScreenCapture targetRef={contentRef}>
        <div className="content-area" ref={contentRef}>
          <h2>Zone de test à capturer</h2>
          <p>Cette zone sera capturée lorsque vous cliquerez sur le bouton ci-dessous.</p>
          
          <div className="test-card">
            <h3>Exemple de dossier</h3>
            <ul>
              <li><strong>Projet:</strong> Valetia</li>
              <li><strong>Date:</strong> 19 mai 2025</li>
              <li><strong>Statut:</strong> En développement</li>
            </ul>
          </div>
        </div>
      </ScreenCapture>
    </div>
  )
}

export default App
