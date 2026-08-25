import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import { useAuth } from '../context/AuthContext.jsx';
import RecipeCard from '../components/RecipeCard.jsx';

export default function Dashboard() {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [recent, setRecent] = useState([]);
  const [cookbooks, setCookbooks] = useState([]);

  useEffect(() => {
    client.get('/recipes/', { params: { favorite: true, page_size: 6 } }).then((r) => setFavorites(r.data.results || r.data));
    client.get('/recipes/', { params: { ordering: '-created_at' } }).then((r) => setRecent((r.data.results || r.data).slice(0, 6)));
    client.get('/cookbooks/').then((r) => setCookbooks(r.data.results || r.data));
  }, []);

  return (
    <div className="page">
      <h1>Bonjour {user?.first_name || user?.username} 👋</h1>
      <p className="subtitle">Voici un aperçu de votre univers culinaire SUPMEAL.</p>

      <section className="section">
        <div className="section-header">
          <h2>Vos cookbooks</h2>
          <Link to="/cookbooks">Voir tout</Link>
        </div>
        <div className="cookbook-strip">
          {cookbooks.length === 0 && <p className="empty">Aucun cookbook pour l'instant.</p>}
          {cookbooks.slice(0, 4).map((cb) => (
            <Link key={cb.id} to={`/cookbooks/${cb.id}`} className="cookbook-chip">
              <strong>{cb.name}</strong>
              <span>{cb.recipe_count} recette(s)</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2>Vos favoris</h2>
          <Link to="/recipes?favorite=true">Voir tout</Link>
        </div>
        <div className="recipe-grid">
          {favorites.length === 0 && <p className="empty">Aucune recette favorite pour le moment.</p>}
          {favorites.map((r) => <RecipeCard key={r.id} recipe={r} />)}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2>Ajoutées récemment</h2>
          <Link to="/recipes">Voir tout</Link>
        </div>
        <div className="recipe-grid">
          {recent.map((r) => <RecipeCard key={r.id} recipe={r} />)}
        </div>
      </section>
    </div>
  );
}
