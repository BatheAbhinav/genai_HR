import { useEffect, useState } from 'react';
import { fetchDocuments } from '../api';

export default function DocumentsPage() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments()
      .then(setDocs)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p aria-busy="true">Loading documents...</p>;
  if (error) return <p style={{ color: 'var(--pico-color-red-500)' }}>{error}</p>;

  return (
    <>
      <h2>Policy Documents</h2>
      {docs.length === 0 ? (
        <p>No documents uploaded yet. Admin can upload PDFs from the Upload page.</p>
      ) : (
        <figure>
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Policy Type</th>
                <th>Version</th>
                <th>Status</th>
                <th>Uploaded By</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.doc_id}>
                  <td>{doc.title}</td>
                  <td>{doc.policy_type}</td>
                  <td>{doc.version}</td>
                  <td>{doc.status}</td>
                  <td>{doc.uploaded_by}</td>
                  <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </figure>
      )}
    </>
  );
}
