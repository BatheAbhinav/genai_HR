import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { uploadDocument } from '../api';

const POLICY_TYPES = [
  { value: 'leave', label: 'Leave' },
  { value: 'insurance', label: 'Insurance' },
  { value: 'hr-guidelines', label: 'HR Guidelines' },
  { value: 'compensation', label: 'Compensation' },
  { value: 'remote-work', label: 'Remote Work' },
  { value: 'labour-law', label: 'Labour Law' },
  { value: 'general', label: 'General' },
];

export default function UploadPage() {
  const { auth } = useAuth();
  const [title, setTitle] = useState('');
  const [policyType, setPolicyType] = useState('leave');  // default to first option
  const [version, setVersion] = useState('v1');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', isError: false });

  if (auth.role !== 'admin') {
    return (
      <>
        <h2>Upload Policy Document</h2>
        <p>Only admin users can upload documents.</p>
      </>
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage({ text: '', isError: false });
    setLoading(true);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('policy_type', policyType);
    formData.append('version', version);
    formData.append('file', file);

    try {
      const result = await uploadDocument(formData);
      setMessage({ text: `Uploaded successfully: ${result.title} (${result.doc_id})`, isError: false });
      setTitle('');
      setVersion('v1');
      setFile(null);
      e.target.reset();
    } catch (err) {
      setMessage({ text: err.message, isError: true });
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h2>Upload Policy Document</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Title
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Leave Policy 2025"
            required
          />
        </label>
        <label>
          Policy Type
          <select value={policyType} onChange={(e) => setPolicyType(e.target.value)}>
            {POLICY_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>
        <label>
          Version
          <input
            type="text"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
          />
        </label>
        <label>
          PDF File
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            required
          />
        </label>
        {message.text && (
          <p style={{ color: message.isError ? 'var(--pico-color-red-500)' : 'var(--pico-color-green-500)' }}>
            {message.text}
          </p>
        )}
        <button type="submit" aria-busy={loading} disabled={loading}>
          {loading ? 'Uploading & Processing...' : 'Upload'}
        </button>
      </form>
    </>
  );
}
