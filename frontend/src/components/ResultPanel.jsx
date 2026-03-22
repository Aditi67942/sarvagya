// src/components/ResultPanel.jsx
import usePipelineStore from '../store/usePipelineStore'
import AudioPlayer from './AudioPlayer'

export default function ResultPanel() {
  const { result, error, loading } = usePipelineStore()

  if (loading) {
    return (
      <div className="result-panel loading">
        <div className="spinner" />
        <p>Running pipeline — OCR · Translation · Braille · TTS</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result-panel error">
        <p>⚠️ {error}</p>
      </div>
    )
  }

  if (!result) return null

  return (
    <div className="result-panel">

      {/* Extracted Text */}
      <div className="result-card">
        <h3 className="section-title">📖 Extracted Text</h3>
        <p className="result-text">{result.ocr?.final_text || '—'}</p>
        <span className="badge">via {result.ocr?.winning_provider}</span>
      </div>

      {/* Translation */}
      <div className="result-card">
        <h3 className="section-title">🌐 English Translation</h3>
        <p className="result-text">{result.translation?.translated_text || '—'}</p>
      </div>

      {/* Braille */}
      <div className="result-card braille-card">
        <h3 className="section-title">⠃⠗⠁⠊⠇⠇⠑ Braille Output</h3>
        <p className="braille-text">{result.braille?.braille_text || '—'}</p>
      </div>

      {/* Audio */}
      <AudioPlayer audioBase64={result.tts?.audio_base64} />

    </div>
  )
}