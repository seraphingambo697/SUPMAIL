import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import client, { API_BASE_URL } from '../api/client';
import { useAuth } from '../context/AuthContext.jsx';

export default function RecipeDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [error, setError] = useState('');

  const load = () => client.get(`/recipes/${id}/`).then((r) => setRecipe(r.data));

  useEffect(() => { load(); }, [id]);

  if (!recipe) return <div className="page"><p className="empty">Chargement…</p></div>;

  const imageUrl = recipe.image
    ? (recipe.image.startsWith('http') ? recipe.image : `${API_BASE_URL.replace('/api', '')}${recipe.image}`)
    : null;

  const toggleFavorite = async () => {
    const { data } = await client.post(`/recipes/${id}/toggle_favorite/`);
    setRecipe({ ...recipe, is_favorite: data.is_favorite });
  };

  const handleDelete = async () => {
    if (!window.confirm('Supprimer définitivement cette recette ?')) return;
    try {
      await client.delete(`/recipes/${id}/`);
      navigate('/recipes');
    } catch {
      setError('Suppression impossible (permission refusée).');
    }
  };

  const postComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    try {
      await client.post(`/recipes/${id}/comments/`, { content: commentText });
      setCommentText('');
      load();
    } catch {
      setError("Vous n'avez pas la permission de commenter ici.");
    }
  };

  const canEdit = recipe.owner?.id === user?.id || recipe.cookbook;

  return (
    <div className="page">
      {error && <p className="error-text">{error}</p>}
      <div className="recipe-detail-header">
        <div className="recipe-detail-image" style={imageUrl ? { backgroundImage: `url(${imageUrl})` } : {}}>
          {!imageUrl && <span>🍽️</span>}
        </div>
        <div className="recipe-detail-info">
          <h1>{recipe.title}</h1>
          <div className="tag-row">
            {recipe.tags.map((t) => <span key={t.id} className="tag-pill">{t.name}</span>)}
          </div>
          <div className="recipe-meta-strip">
            <span>⏱ Préparation : {recipe.prep_time_minutes} min</span>
            <span>🔥 Cuisson : {recipe.cook_time_minutes} min</span>
            <span>🍽 Portions : {recipe.servings}</span>
            {recipe.source && <span>🔗 Source : {recipe.source}</span>}
          </div>
          <div className="btn-row">
            <button className={`btn-fav ${recipe.is_favorite ? 'active' : ''}`} onClick={toggleFavorite}>
              {recipe.is_favorite ? '★ Favori' : '☆ Ajouter aux favoris'}
            </button>
            {canEdit && <Link to={`/recipes/${id}/edit`} className="btn-secondary">Modifier</Link>}
            {canEdit && <button className="btn-danger" onClick={handleDelete}>Supprimer</button>}
          </div>
        </div>
      </div>

      <div className="recipe-detail-body">
        <section>
          <h2>Ingrédients</h2>
          <ul className="ingredient-list">
            {recipe.ingredients.map((i) => (
              <li key={i.id}>{i.quantity} {i.unit} {i.ingredient.name}</li>
            ))}
          </ul>
        </section>
        <section>
          <h2>Étapes</h2>
          <ol className="steps-list">
            {recipe.steps.split('\n').filter(Boolean).map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </section>
      </div>

      {recipe.cookbook && (
        <section className="section">
          <h2>Commentaires</h2>
          <div className="comments-list">
            {recipe.comments.length === 0 && <p className="empty">Aucun commentaire pour l'instant.</p>}
            {recipe.comments.map((c) => (
              <div key={c.id} className="comment-item">
                <strong>{c.author.username}</strong>
                <span className="comment-date">{new Date(c.created_at).toLocaleString('fr-FR')}</span>
                <p>{c.content}</p>
              </div>
            ))}
          </div>
          <form onSubmit={postComment} className="comment-form">
            <input
              placeholder="Ajouter un commentaire, un conseil…"
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
            />
            <button className="btn-primary" type="submit">Envoyer</button>
          </form>
        </section>
      )}
    </div>
  );
}
