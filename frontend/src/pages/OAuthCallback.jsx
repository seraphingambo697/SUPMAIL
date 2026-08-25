import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext.jsx';

export default function OAuthCallback() {
  const { provider } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { loginWithTokens } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = params.get('code');
    if (!code) {
      setError('Code OAuth2 manquant.');
      return;
    }
    const redirectUri = `${window.location.origin}/oauth/callback/${provider}`;
    client
      .post(`/auth/oauth/${provider}/`, { code, redirect_uri: redirectUri })
      .then(async ({ data }) => {
        await loginWithTokens(data.access, data.refresh, data.user);
        navigate('/');
      })
      .catch(() => setError("Échec de la connexion OAuth2. Le fournisseur est peut-être mal configuré côté serveur."));
  }, [params, provider]);

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Connexion via {provider}…</h1>
        {error ? <p className="error-text">{error}</p> : <p>Merci de patienter…</p>}
      </div>
    </div>
  );
}
