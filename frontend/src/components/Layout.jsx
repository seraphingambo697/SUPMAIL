import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">🍲</span>
          <span className="brand-name">SUPMEAL</span>
        </div>
        <nav className="nav">
          <NavLink to="/" end>Tableau de bord</NavLink>
          <NavLink to="/recipes">Recettes</NavLink>
          <NavLink to="/cookbooks">Cookbooks</NavLink>
          <NavLink to="/planner">Planning</NavLink>
          <NavLink to="/import-export">Import / Export</NavLink>
          <NavLink to="/settings">Paramètres</NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip">
            <div className="avatar-circle">{user?.username?.[0]?.toUpperCase()}</div>
            <span>{user?.username}</span>
          </div>
          <button className="btn-ghost" onClick={handleLogout}>Déconnexion</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
