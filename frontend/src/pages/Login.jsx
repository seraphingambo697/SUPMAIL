import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

const OAUTH_CONFIG = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
    scope: 'openid email profile',
  },
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    clientId: import.meta.env.VITE_GITHUB_CLIENT_ID || '',
    scope: 'read:user user:email',
  },
  microsoft: {
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    clientId: import.meta.env.VITE_MICROSOFT_CLIENT_ID || '',
    scope: 'openid email profile',
  },
};

function startOAuth(provider) {
  const config = OAUTH_CONFIG[provider];
  const redirectUri = `${window.location.origin}/oauth/callback/${provider}`;
  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: config.scope,
  });
  window.location.href = `${config.authUrl}?${params.toString()}`;
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError("Identifiants incorrects.");
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
        <h1>Connexion</h1>
        <form onSubmit={handleSubmit} className="form">
          <label>Nom d'utilisateur</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          <label>Mot de passe</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="error-text">{error}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>
        <div className="divider">ou</div>
        <div className="oauth-buttons">
          <button className="btn-oauth google" onClick={() => startOAuth('google')}>Continuer avec Google</button>
          <button className="btn-oauth github" onClick={() => startOAuth('github')}>Continuer avec GitHub</button>
          <button className="btn-oauth microsoft" onClick={() => startOAuth('microsoft')}>Continuer avec Microsoft</button>
        </div>
        <p className="auth-switch">
          Pas encore de compte ? <Link to="/register">S'inscrire</Link>
        </p>
      </div>
    </div>
  );
}
