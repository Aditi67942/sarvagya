return (
  <div className="result-panel">

    {/* Extracted Text */}
    <div className="result-card">
      <h3 className="section-title">📖 Extracted Text</h3>
      <p className="result-text">{result.ocr_text || '—'}</p>
    </div>

    {/* Translation */}
    <div className="result-card">
      <h3 className="section-title">🌐 English Translation</h3>
      <p className="result-text">{result.translated_text || '—'}</p>
    </div>

    {/* Braille */}
    <div className="result-card braille-card">
      <h3 className="section-title">⠃⠗⠁⠊⠇⠇⠑ Braille Output</h3>
      <p className="braille-text">{result.braille_text || '—'}</p>
    </div>

    {/* Audio */}
    <AudioPlayer audioBase64={result.audio_base64} />

  </div>
)