import { useState } from 'react';
import { queryPolicy } from '../api';

const POLICY_TYPES = [
  { value: '', label: 'All policies' },
  { value: 'leave', label: 'Leave' },
  { value: 'health_insurance', label: 'Health Insurance' },
  { value: 'remote_work', label: 'Remote Work' },
];

export default function QueryPage() {
  const [question, setQuestion] = useState('');
  const [policyType, setPolicyType] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const data = await queryPolicy(question, policyType || null);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function askFollowUp(q) {
    setQuestion(q);
    setResult(null);
  }

  return (
    <>
      <h2>Ask a Question</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Your Question
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder='e.g. "How many casual leaves can I carry forward?"'
            required
            autoFocus
          />
        </label>
        <label>
          Filter by Policy Type (optional)
          <select value={policyType} onChange={(e) => setPolicyType(e.target.value)}>
            {POLICY_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>
        {error && <p style={{ color: 'var(--pico-color-red-500)' }}>{error}</p>}
        <button type="submit" aria-busy={loading} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {result && (
        <article style={{ marginTop: '2rem' }}>
          {result.escalation_required && (
            <div style={{
              background: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: 8,
              padding: '0.75rem 1rem',
              marginBottom: '1rem',
            }}>
              <strong>Escalation Required:</strong> This question may need HR review. Please contact your HR representative for further assistance.
            </div>
          )}

          <header>
            <h3>Answer</h3>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.9rem' }}>
              <span>
                Confidence: <strong>{(result.confidence * 100).toFixed(0)}%</strong>
              </span>
              <span style={{ opacity: 0.5 }}>|</span>
              <span style={{ opacity: 0.6 }}>ID: {result.request_id.slice(0, 8)}</span>
            </div>
          </header>

          <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{result.answer}</p>

          {result.citations.length > 0 && (
            <>
              <h4>Sources</h4>
              {result.citations.map((c, i) => (
                <details key={i} style={{ marginBottom: '0.5rem' }}>
                  <summary>
                    {c.title} {c.page != null && `(Page ${c.page})`} {c.section && `- ${c.section}`} <small>[{c.version}]</small>
                  </summary>
                  <blockquote style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                    {c.snippet}
                  </blockquote>
                </details>
              ))}
            </>
          )}

          {result.follow_up_questions.length > 0 && (
            <>
              <h4>Follow-up Questions</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {result.follow_up_questions.map((q, i) => (
                  <button
                    key={i}
                    className="outline"
                    style={{ fontSize: '0.85rem' }}
                    onClick={() => askFollowUp(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </>
          )}
        </article>
      )}
    </>
  );
}
