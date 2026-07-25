import { useState, useRef, useEffect } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function splitResponse(fullResponse) {
  const match = fullResponse.match(/<think>([\s\S]*?)<\/think>/)
  if (match) {
    const thinking = match[1].trim()
    const answer = fullResponse.replace(/<think>[\s\S]*?<\/think>/, '').trim()
    return { thinking, answer }
  }
  return { thinking: null, answer: fullResponse.trim() }
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const [files, setFiles] = useState([])
  const [indexedFiles, setIndexedFiles] = useState([])
  const [indexing, setIndexing] = useState(false)
  const [thresholds, setThresholds] = useState(null)

  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    fetch(`${API_BASE}/thresholds`).then(r => r.json()).then(setThresholds).catch(() => {})
    fetch(`${API_BASE}/indexed-files`).then(r => r.json()).then(d => setIndexedFiles(d.indexed_files || [])).catch(() => {})
  }, [])

  async function handleIndex() {
    if (files.length === 0 || indexing) return
    setIndexing(true)
    const formData = new FormData()
    for (const f of files) formData.append('files', f)

    try {
      const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData })
      const data = await res.json()
      setIndexedFiles(data.indexed_files || [])
      setFiles([])
    } catch (err) {
      alert(`Indexing failed: ${err.message}`)
    } finally {
      setIndexing(false)
    }
  }

  async function sendMessage() {
    const question = input.trim()
    if (!question || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json()

      const { thinking, answer } = splitResponse(data.answer || '')

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: answer,
          thinking,
          sources: data.sources || [],
          trace: data.trace || {}
        }
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `⚠️ Could not reach backend API: ${err.message}` }
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={styles.app}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <h3>📁 Document Upload</h3>
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          onChange={(e) => setFiles(Array.from(e.target.files))}
          style={styles.fileInput}
        />
        <button
          onClick={handleIndex}
          disabled={files.length === 0 || indexing}
          style={styles.indexButton}
        >
          {indexing ? 'Indexing...' : 'Index Documents'}
        </button>

        {indexedFiles.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <strong>Currently indexed:</strong>
            <ul style={styles.fileList}>
              {indexedFiles.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
        )}

        <hr style={styles.divider} />

        <strong>Current thresholds</strong>
        {thresholds && (
          <div style={styles.thresholdsBox}>
            <div>UT: {thresholds.upper_threshold}</div>
            <div>LT: {thresholds.lower_threshold}</div>
            <div>Strip: {thresholds.strip_threshold}</div>
          </div>
        )}
      </div>

      {/* Main chat area */}
      <div style={styles.main}>
        <h2>💬 Corrective RAG (CRAG)</h2>

        <div style={styles.chatBox}>
          {messages.length === 0 && (
            <p style={styles.empty}>Ask a question about your documents...</p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.bubble,
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                background: msg.role === 'user' ? '#1E88E5' : '#F5F5F5',
                color: msg.role === 'user' ? '#fff' : '#111'
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

              {msg.thinking && (
                <details style={styles.expander}>
                  <summary>🧠 Model Reasoning</summary>
                  <div style={{ whiteSpace: 'pre-wrap', marginTop: 6 }}>{msg.thinking}</div>
                </details>
              )}

              {msg.role === 'assistant' && (
                <details style={styles.expander}>
                  <summary>📄 Sources</summary>
                  {msg.sources && msg.sources.length > 0 ? (
                    <ul>
                      {msg.sources.map((s, j) => (
                        <li key={j}>
                          {s.source || s.url || 'unknown'}
                          {s.strips_used && (
                            <ul>
                              {s.strips_used.map((strip, k) => <li key={k} style={{ fontSize: 12, color: '#666' }}>{strip}</li>)}
                            </ul>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div>No sources were used (fallback).</div>
                  )}
                </details>
              )}

              {msg.trace && Object.keys(msg.trace).length > 0 && (
                <details style={styles.expander}>
                  <summary>🔍 Pipeline Trace (Internal Details)</summary>

                  <div style={{ marginTop: 8 }}>
                    <strong>📄 Retrieved Chunks</strong>
                    {(msg.trace.retrieved_chunks || []).map((c, idx) => (
                      <div key={idx} style={styles.traceItem}>
                        <b>{c.source}</b> (ID: {c.id})<br />
                        <span style={{ color: '#666' }}>Preview: {c.text_preview}...</span>
                      </div>
                    ))}
                  </div>

                  <div style={{ marginTop: 8 }}>
                    <strong>Chunk Scores</strong>
                    {(msg.trace.chunk_scores || []).map((s, idx) => (
                      <div key={idx}>{s.source}: <b>{s.score}</b></div>
                    ))}
                  </div>

                  <div style={{ marginTop: 8 }}>
                    <strong>Classification: {msg.trace.classification}</strong>
                    <div style={styles.classificationBanner(msg.trace.classification)}>
                      {msg.trace.classification === 'correct' && '✅ Using local documents only'}
                      {msg.trace.classification === 'ambiguous' && '⚠️ Ambiguous – refined local chunks + web search'}
                      {msg.trace.classification === 'incorrect' && '❌ Incorrect – web search only'}
                    </div>
                  </div>

                  {msg.trace.refined_local && msg.trace.refined_local.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <strong>Refined Local Chunks</strong>
                      {msg.trace.refined_local.map((r, idx) => (
                        <div key={idx} style={styles.traceItem}>
                          {r.chunk_id}: kept <b>{r.strips_kept}</b> strips<br />
                          <span style={{ color: '#666' }}>Preview: {r.preview}...</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {msg.trace.web_search_used && (
                    <div style={{ marginTop: 8 }}>
                      <strong>🌐 Web Search</strong>
                      <div>Rewritten query: <code>{msg.trace.rewritten_query || 'N/A'}</code></div>
                      {(msg.trace.web_results || []).map((w, idx) => (
                        <div key={idx} style={styles.traceItem}>
                          <a href={w.url} target="_blank" rel="noreferrer">{w.title}</a><br />
                          <span style={{ color: '#666' }}>Preview: {w.preview}...</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div style={{ marginTop: 8 }}>
                    <strong>📝 Final Context Preview</strong>
                    <pre style={styles.contextPreview}>{msg.trace.final_context || 'No context generated.'}</pre>
                  </div>
                </details>
              )}
            </div>
          ))}

          {loading && <div style={styles.loading}>Thinking...</div>}
          <div ref={bottomRef} />
        </div>

        <div style={styles.inputRow}>
          <textarea
            style={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={2}
          />
          <button style={styles.sendButton} onClick={sendMessage} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

const styles = {
  app: { display: 'flex', height: '100vh', fontFamily: 'sans-serif' },
  sidebar: {
    width: 260,
    padding: 20,
    borderRight: '1px solid #ddd',
    overflowY: 'auto',
    background: '#fafafa'
  },
  fileInput: { display: 'block', marginBottom: 10, fontSize: 12 },
  indexButton: {
    width: '100%',
    padding: 8,
    background: '#1E88E5',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer'
  },
  fileList: { paddingLeft: 18, fontSize: 13 },
  divider: { margin: '16px 0', border: 'none', borderTop: '1px solid #ddd' },
  thresholdsBox: {
    marginTop: 8,
    padding: 10,
    background: '#E3F2FD',
    borderRadius: 6,
    fontSize: 13
  },
  main: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    padding: 20,
    boxSizing: 'border-box',
    minWidth: 0
  },
  chatBox: {
    flex: 1,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
    padding: 10,
    border: '1px solid #ddd',
    borderRadius: 8
  },
  empty: { color: '#888', textAlign: 'center', marginTop: 40 },
  bubble: {
    maxWidth: '85%',
    padding: '10px 14px',
    borderRadius: 12
  },
  expander: {
    marginTop: 8,
    fontSize: 13,
    background: 'rgba(0,0,0,0.03)',
    borderRadius: 6,
    padding: 8
  },
  traceItem: { marginTop: 6, fontSize: 13 },
  contextPreview: {
    whiteSpace: 'pre-wrap',
    background: '#f0f0f0',
    padding: 8,
    borderRadius: 6,
    fontSize: 12,
    maxHeight: 200,
    overflowY: 'auto'
  },
  classificationBanner: (classification) => ({
    marginTop: 4,
    padding: 8,
    borderRadius: 6,
    background:
      classification === 'correct' ? '#E8F5E9' :
      classification === 'ambiguous' ? '#FFF8E1' : '#FFEBEE',
    fontSize: 13
  }),
  loading: { color: '#888', fontStyle: 'italic' },
  inputRow: { display: 'flex', gap: 8, marginTop: 12 },
  textarea: {
    flex: 1,
    padding: 10,
    borderRadius: 8,
    border: '1px solid #ccc',
    resize: 'none',
    fontSize: 14
  },
  sendButton: {
    padding: '0 20px',
    borderRadius: 8,
    border: 'none',
    background: '#1E88E5',
    color: '#fff',
    fontSize: 14,
    cursor: 'pointer'
  }
}