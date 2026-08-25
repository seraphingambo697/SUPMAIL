import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../api/client';

export default function RecipeCard({ recipe }) {
  const imageUrl = recipe.image
    ? (recipe.image.startsWith('http') ? recipe.image : `${API_BASE_URL.replace('/api', '')}${recipe.image}`)
    : null;

  return (
    <Link to={`/recipes/${recipe.id}`} className="recipe-card">
      <div className="recipe-card-image" style={imageUrl ? { backgroundImage: `url(${imageUrl})` } : {}}>
        {!imageUrl && <span>🍽️</span>}
        {recipe.is_favorite && <span className="fav-badge">★</span>}
      </div>
      <div className="recipe-card-body">
        <h3>{recipe.title}</h3>
        <div className="recipe-card-meta">
          <span>⏱ {recipe.total_time_minutes ?? (recipe.prep_time_minutes + recipe.cook_time_minutes)} min</span>
          <span>🍽 {recipe.servings} pers.</span>
        </div>
        <div className="tag-row">
          {(recipe.tags || []).slice(0, 3).map((t) => (
            <span key={t.id} className="tag-pill">{t.name}</span>
          ))}
        </div>
      </div>
    </Link>
  );
}
