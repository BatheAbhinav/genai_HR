import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DocumentsPage from './pages/DocumentsPage';
import UploadPage from './pages/UploadPage';
import QueryPage from './pages/QueryPage';

function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/query" element={<QueryPage />} />
            <Route path="/" element={<Navigate to="/documents" replace />} />
          </Route>
        </Routes>
      </main>
    </>
  );
}

export default App;
