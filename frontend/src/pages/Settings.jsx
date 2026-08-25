import { useEffect, useState } from 'react';
import client from '../api/client';
import { useAuth } from '../context/AuthContext.jsx';

const DIETS = [
  ['none', 'Aucun'], ['vegetarian', 'Végétarien'], ['vegan', 'Végétalien'],
  ['pescatarian', 'Pescétarien'], ['gluten_free', 'Sans gluten'], ['halal', 'Halal'], ['kosher', 'Casher'],
];

export default function Settings() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState(null);
  const [savedMsg, setSavedMsg] = useState('');
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState('');

  useEffect(() => { if (user) setForm(user); }, [user]);

  if (!form) return null;

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const saveProfile = async (e) => {
    e.preventDefault();
    const { data } = await client.patch('/auth/me/', {
      first_name: form.first_name,
      last_name: form.last_name,
      diet: form.diet,
      allergies: form.allergies,
      favorite_cuisine: form.favorite_cuisine,
      default_servings: form.default_servings,
    });
    setUser(data);
    setSavedMsg('Profil mis à jour.');
    setTimeout(() => setSavedMsg(''), 2500);
  };

  const changePassword = async (e) => {
    e.preventDefault();
    setPwError('');
    setPwSuccess('');
    try {
      await client.post('/auth/me/change-password/', { old_password: oldPassword, new_password: newPassword });
      setPwSuccess('Mot de passe modifié.');
      setOldPassword('');
      setNewPassword('');
    } catch (err) {
      setPwError(err.response?.data?.detail || 'Erreur lors du changement de mot de passe.');
    }
  };

  return (
    <div className="page">
      <h1>Paramètres</h1>

      <section className="section card">
        <h2>Profil & préférences culinaires</h2>
        <form onSubmit={saveProfile} className="form">
          <div className="form-row">
            <div>
              <label>Prénom</label>
              <input value={form.first_name || ''} onChange={update('first_name')} />
            </div>
            <div>
              <label>Nom</label>
              <input value={form.last_name || ''} onChange={update('last_name')} />
            </div>
          </div>
          <label>Régime alimentaire</label>
          <select value={form.diet} onChange={update('diet')}>
            {DIETS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <label>Allergies (séparées par des virgules)</label>
          <input value={form.allergies || ''} onChange={update('allergies')} />
          <label>Cuisine préférée</label>
          <input value={form.favorite_cuisine || ''} onChange={update('favorite_cuisine')} />
          <label>Nombre de portions par défaut</label>
          <input type="number" min="1" value={form.default_servings} onChange={update('default_servings')} />
          {savedMsg && <p className="success-text">{savedMsg}</p>}
          <button className="btn-primary" type="submit">Enregistrer</button>
        </form>
      </section>

      {!user.oauth_provider && (
        <section className="section card">
          <h2>Changer de mot de passe</h2>
          <form onSubmit={changePassword} className="form">
            <label>Mot de passe actuel</label>
            <input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} required />
            <label>Nouveau mot de passe</label>
            <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
            {pwError && <p className="error-text">{pwError}</p>}
            {pwSuccess && <p className="success-text">{pwSuccess}</p>}
            <button className="btn-primary" type="submit">Mettre à jour</button>
          </form>
        </section>
      )}
    </div>
  );
}
