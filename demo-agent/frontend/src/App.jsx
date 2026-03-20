import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

/* ── Sub-components ──────────────────────────────────────────────────────── */

function TripCard({ option, isPrimary }) {
  const cls = isPrimary ? 'trip-card' : 'trip-card alt'
  return (
    <div className={cls}>
      <span className="rank-badge">
        {isPrimary ? '★ Recommended' : `Option ${option.rank}`}
      </span>
      <h3>
        {option.flight.label} + {option.hotel.name}
      </h3>
      <div className="field">
        <span className="field-label">Outbound</span>
        <span>
          {option.flight.origin} → {option.flight.destination} &nbsp;
          dep {option.flight.departure_time}
        </span>
      </div>
      {option.flight.return_label && (
        <div className="field">
          <span className="field-label">Return</span>
          <span>
            {option.flight.return_origin} → {option.flight.return_destination} &nbsp;
            dep {option.flight.return_departure_time}
          </span>
        </div>
      )}
      <div className="field">
        <span className="field-label">Hotel</span>
        <span>
          {option.hotel.name} ({option.hotel.area || 'Area unavailable'}), {option.hotel.nights} night(s)
          @ ${option.hotel.nightly_rate_usd.toFixed(0)}/night
        </span>
      </div>
      <div className="field">
        <span className="field-label">Flights Total</span>
        <span>${option.flight.price_usd.toFixed(0)}</span>
      </div>
      <div className="field">
        <span className="field-label">Est. Total</span>
        <span style={{ color: 'var(--green)', fontWeight: 600 }}>
          ${option.estimated_total_usd.toFixed(0)}
        </span>
      </div>
      {option.why && option.why.length > 0 && (
        <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
          {option.why.map((r, i) => (
            <div key={i}>• {r}</div>
          ))}
        </div>
      )}
    </div>
  )
}

function PaymentTracePanel({ spend }) {
  if (!spend || spend.length === 0) return null
  return (
    <div className="payment-trace">
      <h4>Tempo Payment Trace</h4>
      {spend.map((s, i) => (
        <div key={i} className="trace-row">
          <span className="svc">{s.service_name}</span>
          <span className="amt">{s.amount.toFixed(2)} {s.token}</span>
          <span className="hash" title={s.tx_hash}>
            tx: {s.tx_hash.slice(0, 18)}…
          </span>
        </div>
      ))}
    </div>
  )
}

function AuditLog({ log }) {
  const [open, setOpen] = useState(false)
  if (!log || log.length === 0) return null
  return (
    <>
      <span className="audit-toggle" onClick={() => setOpen(!open)}>
        {open ? '▾ Hide' : '▸ Show'} audit log ({log.length} entries)
      </span>
      {open && (
        <div className="audit-panel">
          {log.map((e, i) => (
            <div key={i}>
              [{e.timestamp}] {e.event} {JSON.stringify(e.data)}
            </div>
          ))}
        </div>
      )}
    </>
  )
}

function AgentMessage({ data }) {
  return (
    <div className="message agent">
      <div className="message-label">Agent</div>
      <div className="message-bubble">
        {data.summary && <ReactMarkdown>{data.summary}</ReactMarkdown>}

        {data.recommended_option && (
          <TripCard option={data.recommended_option} isPrimary />
        )}

        {data.alternatives &&
          data.alternatives.map((alt) => (
            <TripCard key={alt.rank} option={alt} />
          ))}

        <PaymentTracePanel spend={data.search_spend} />
        <AuditLog log={data.audit_log} />
      </div>
    </div>
  )
}

/* ── Main App ────────────────────────────────────────────────────────────── */

const SAMPLE_PROMPT =
  'Find me hotels and a flight to a conference in New York, Dec 28-29. Depart from SFO. No red-eyes. Keep it under $700 total.'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [network, setNetwork] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    let cancelled = false
    async function loadNetwork() {
      try {
        const res = await fetch('/api/network')
        if (!res.ok) return
        const data = await res.json()
        if (!cancelled) setNetwork(data)
      } catch (_) {
        // best-effort only
      }
    }
    loadNetwork()
    return () => {
      cancelled = true
    }
  }, [])

  async function send() {
    const text = input.trim()
    if (!text || loading) return

    setMessages((prev) => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      if (!res.ok) {
        const body = await res.text()
        throw new Error(`Request failed (${res.status}): ${body}`)
      }
      const data = await res.json()
      setMessages((prev) => [...prev, { role: 'agent', data }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'agent', data: { summary: `**Error**: ${err.message}`, status: 'error' } },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <>
      <header className="app-header">
        <h1>Conference Trip Agent</h1>
        <span className="badge">Tempo Demo</span>
      </header>

      {network && (
        <div
          style={{
            margin: '0 auto 8px',
            maxWidth: 980,
            color: 'var(--text-muted)',
            fontSize: 12,
            padding: '0 20px',
          }}
        >
          Network: {network.connected ? 'connected' : 'offline'} · mode: {network.resolved_mode} · chain:{' '}
          {network.chain_id ?? network.expected_chain_id} · wallet: {network.wallet_address || 'not configured'}
          {typeof network.wallet_pathusd_balance === 'number' && (
            <> · pathUSD: {network.wallet_pathusd_balance.toFixed(4)}</>
          )}
        </div>
      )}

      <div className="chat-container">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: 80 }}>
            <p style={{ fontSize: 15, marginBottom: 12 }}>
              Ask me to plan a conference trip. I'll search flights and hotels,
              pay for search services with Tempo, and recommend the best options.
            </p>
            <button
              style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                color: 'var(--text)',
                padding: '8px 16px',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                fontSize: 13,
              }}
              onClick={() => setInput(SAMPLE_PROMPT)}
            >
              Try sample prompt
            </button>
          </div>
        )}

        {messages.map((msg, i) =>
          msg.role === 'user' ? (
            <div key={i} className="message user">
              <div className="message-label">You</div>
              <div className="message-bubble">{msg.text}</div>
            </div>
          ) : (
            <AgentMessage key={i} data={msg.data} />
          ),
        )}

        {loading && <div className="status-indicator">Searching & paying with Tempo…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Describe your conference trip…"
          disabled={loading}
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </>
  )
}
