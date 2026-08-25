import { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext.jsx';
import RecipeCard from '../components/RecipeCard.jsx';

export default function CookbookDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [cookbook, setCookbook] = useState(null);
  const [tab, setTab] = useState('recipes');
  const [recipes, setRecipes] = useState([]);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('reader');
  const pollRef = useRef(null);

  const loadCookbook = () => client.get(`/cookbooks/${id}/`).then((r) => setCookbook(r.data));
  const loadRecipes = () => client.get('/recipes/', { params: { cookbook: id } }).then((r) => setRecipes(r.data.results || r.data));

  useEffect(() => {
    loadCookbook();
    loadRecipes();
  }, [id]);

  useEffect(() => {
    if (tab !== 'chat') return;
    const fetchMessages = () => {
      const after = messages.length ? messages[messages.length - 1].id : undefined;
      client.get('/messages/', { params: { cookbook: id, after } }).then((r) => {
        const newOnes = r.data.results || r.data;
        if (newOnes.length) setMessages((prev) => [...prev, ...newOnes]);
      });
    };
    client.get('/messages/', { params: { cookbook: id } }).then((r) => setMessages(r.data.results || r.data));
    pollRef.current = setInterval(fetchMessages, 3000);
    return () => clearInterval(pollRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, id]);

  const runSearch = async () => {
    const { data } = await client.get(`/cookbooks/${id}/search/`, { params: { q: query } });
    setRecipes(data);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    const { data } = await client.post('/messages/', { cookbook: id, content: messageText });
    setMessages((prev) => [...prev, data]);
    setMessageText('');
  };

  const sendInvite = async (e) => {
    e.preventDefault();
    await client.post(`/cookbooks/${id}/invite/`, { email: inviteEmail, role: inviteRole });
    setInviteEmail('');
    loadCookbook();
  };

  const removeMember = async (userId) => {
    await client.post(`/cookbooks/${id}/members/${userId}/remove/`);
    loadCookbook();
  };

  const changeRole = async (userId, role) => {
    await client.post(`/cookbooks/${id}/members/${userId}/role/`, { role });
    loadCookbook();
  };

  if (!cookbook) return <div className="page"><p className="empty">Chargement…</p></div>;

  const canEdit = cookbook.my_role === 'creator' || cookbook.my_role === 'editor';
  const isCreator = cookbook.my_role === 'creator';

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>{cookbook.name}</h1>
          <p className="subtitle">{cookbook.description}</p>
        </div>
        {canEdit && <Link to="/recipes/new" className="btn-primary">+ Ajouter une recette</Link>}
      </div>

      <div className="tabs">
        <button className={tab === 'recipes' ? 'active' : ''} onClick={() => setTab('recipes')}>Recettes</button>
        <button className={tab === 'members' ? 'active' : ''} onClick={() => setTab('members')}>Membres</button>
        <button className={tab === 'chat' ? 'active' : ''} onClick={() => setTab('chat')}>Messagerie</button>
      </div>

      {tab === 'recipes' && (
        <div>
          <div className="filter-bar">
            <input
              className="search-input"
              placeholder="Rechercher dans ce cookbook (titre, ingrédients, tags…)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && runSearch()}
            />
            <button className="btn-secondary" onClick={runSearch}>Rechercher</button>
            <button className="btn-ghost" onClick={loadRecipes}>Réinitialiser</button>
          </div>
          <div className="recipe-grid">
            {recipes.length === 0 && <p className="empty">Aucune recette dans ce cookbook.</p>}
            {recipes.map((r) => <RecipeCard key={r.id} recipe={r} />)}
          </div>
        </div>
      )}

      {tab === 'members' && (
        <div className="section">
          <table className="member-table">
            <thead>
              <tr><th>Membre</th><th>Rôle</th>{isCreator && <th>Actions</th>}</tr>
            </thead>
            <tbody>
              {cookbook.memberships.map((m) => (
                <tr key={m.id}>
                  <td>{m.user.username}</td>
                  <td>
                    {isCreator && m.role !== 'creator' ? (
                      <select value={m.role} onChange={(e) => changeRole(m.user.id, e.target.value)}>
                        <option value="editor">Éditeur</option>
                        <option value="commentator">Commentateur</option>
                        <option value="reader">Lecteur</option>
                      </select>
                    ) : (
                      <span className="role-badge">{m.role}</span>
                    )}
                  </td>
                  {isCreator && (
                    <td>
                      {m.role !== 'creator' && (
                        <button className="btn-ghost" onClick={() => removeMember(m.user.id)}>Retirer</button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>

          {canEdit && (
            <form onSubmit={sendInvite} className="inline-form">
              <input
                type="email"
                placeholder="E-mail à inviter"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
              />
              <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)}>
                <option value="reader">Lecteur</option>
                <option value="commentator">Commentateur</option>
                <option value="editor">Éditeur</option>
              </select>
              <button className="btn-primary" type="submit">Inviter</button>
            </form>
          )}
        </div>
      )}

      {tab === 'chat' && (
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.length === 0 && <p className="empty">Aucun message. Lancez la discussion !</p>}
            {messages.map((m) => (
              <div key={m.id} className={`chat-message ${m.author.id === user.id ? 'own' : ''}`}>
                <strong>{m.author.username}</strong>
                <p>{m.content}</p>
                <span className="comment-date">{new Date(m.created_at).toLocaleTimeString('fr-FR')}</span>
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="comment-form">
            <input
              placeholder="Écrire un message au groupe…"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
            />
            <button className="btn-primary" type="submit">Envoyer</button>
          </form>
        </div>
      )}
    </div>
  );
}
