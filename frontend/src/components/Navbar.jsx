import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { auth, logout } = useAuth();
  if (!auth) return null;

  return (
    <nav className="container-fluid">
      <ul>
        <li><strong>Policy Search</strong></li>
      </ul>
      <ul>
        <li><NavLink to="/documents">Documents</NavLink></li>
        {auth.role === 'admin' && (
          <li><NavLink to="/upload">Upload</NavLink></li>
        )}
        <li><NavLink to="/query">Ask a Question</NavLink></li>
        <li>
          <small>
            {auth.userId} ({auth.role})
          </small>
        </li>
        <li>
          <button className="outline secondary" onClick={logout}>
            Logout
          </button>
        </li>
      </ul>
    </nav>
  );
}
