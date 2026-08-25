import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(' ') : "Erreur lors de l'inscription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="brand center">
          <span className="brand-icon">🍲</span>
          <span className="brand-name">SUPMEAL</span>
        </div>
        <h1>Créer un compte</h1>
        <form onSubmit={handleSubmit} className="form">
          <label>Nom d'utilisateur</label>
          <input value={form.username} onChange={update('username')} required />
          <label>E-mail</label>
          <input type="email" value={form.email} onChange={update('email')} required />
          <div className="form-row">
            <div>
              <label>Prénom</label>
              <input value={form.first_name} onChange={update('first_name')} />
            </div>
            <div>
              <label>Nom</label>
              <input value={form.last_name} onChange={update('last_name')} />
            </div>
          </div>
          <label>Mot de passe</label>
          <input type="password" value={form.password} onChange={update('password')} required />
          {error && <p className="error-text">{error}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Création…' : 'Créer mon compte'}
          </button>
        </form>
        <p className="auth-switch">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
