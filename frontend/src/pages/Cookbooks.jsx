import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';

export default function Cookbooks() {
  const [cookbooks, setCookbooks] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [showForm, setShowForm] = useState(false);

  const load = () => {
    client.get('/cookbooks/').then((r) => setCookbooks(r.data.results || r.data));
    client.get('/invitations/').then((r) => setInvitations(r.data.results || r.data));
  };

  useEffect(() => { load(); }, []);

  const createCookbook = async (e) => {
    e.preventDefault();
    await client.post('/cookbooks/', { name, description });
    setName('');
    setDescription('');
    setShowForm(false);
    load();
  };

  const acceptInvitation = async (invId) => {
    await client.post(`/invitations/${invId}/accept/`);
    load();
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Cookbooks</h1>
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Annuler' : '+ Nouveau cookbook'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={createCookbook} className="form inline-form">
          <input placeholder="Nom du cookbook" value={name} onChange={(e) => setName(e.target.value)} required />
          <input placeholder="Description (optionnel)" value={description} onChange={(e) => setDescription(e.target.value)} />
          <button className="btn-primary" type="submit">Créer</button>
        </form>
      )}

      {invitations.length > 0 && (
        <section className="section">
          <h2>Invitations en attente</h2>
          {invitations.map((inv) => (
            <div key={inv.id} className="invitation-item">
              <span>Invitation à rejoindre un cookbook en tant que <strong>{inv.role}</strong></span>
              <button className="btn-secondary" onClick={() => acceptInvitation(inv.id)}>Accepter</button>
            </div>
          ))}
        </section>
      )}

      <div className="cookbook-grid">
        {cookbooks.length === 0 && <p className="empty">Vous n'avez rejoint aucun cookbook pour l'instant.</p>}
        {cookbooks.map((cb) => (
          <Link key={cb.id} to={`/cookbooks/${cb.id}`} className="cookbook-card">
            <h3>{cb.name}</h3>
            <p>{cb.description || 'Pas de description.'}</p>
            <div className="cookbook-card-footer">
              <span>{cb.recipe_count} recette(s)</span>
              <span>{cb.memberships.length} membre(s)</span>
              <span className="role-badge">{cb.my_role}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
