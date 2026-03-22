// src/App.jsx
import FileUpload from './components/FileUpload'
import ResultPanel from './components/ResultPanel'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <h1 className="app-title">सर्वज्ञ · Sarvagya</h1>
        <p className="app-subtitle">
          Assistive Reading Platform — OCR · Translation · Braille · Speech
        </p>
      </header>

      <main className="main">
        <FileUpload />
        <ResultPanel />
      </main>
    </div>
  )
}