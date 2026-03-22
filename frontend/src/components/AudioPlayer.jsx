// src/components/AudioPlayer.jsx
export default function AudioPlayer({ audioBase64 }) {
  if (!audioBase64) return null

  const src = `data:audio/wav;base64,${audioBase64}`

  return (
    <div className="audio-section">
      <h3 className="section-title">🔊 Audio</h3>
      <audio controls src={src} className="audio-player">
        Your browser does not support audio playback.
      </audio>
    </div>
  )
}