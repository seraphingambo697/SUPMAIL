import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import client from '../api/client';
import RecipeCard from '../components/RecipeCard.jsx';

export default function Recipes() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [recipes, setRecipes] = useState([]);
  const [cookbooks, setCookbooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [cookbook, setCookbook] = useState(searchParams.get('cookbook') || '');
  const [tag, setTag] = useState(searchParams.get('tag') || '');
  const [maxPrep, setMaxPrep] = useState(searchParams.get('max_prep_time') || '');
  const [maxCook, setMaxCook] = useState(searchParams.get('max_cook_time') || '');
  const [favoriteOnly, setFavoriteOnly] = useState(searchParams.get('favorite') === 'true');
  const [ingredient, setIngredient] = useState(searchParams.get('ingredient') || '');

  useEffect(() => {
    client.get('/cookbooks/').then((r) => setCookbooks(r.data.results || r.data));
    client.get('/tags/').then((r) => setTags(r.data.results || r.data));
  }, []);

  const runSearch = () => {
    const params = {};
    if (search) params.search = search;
    if (cookbook) params.cookbook = cookbook;
    if (tag) params.tag = tag;
    if (maxPrep) params.max_prep_time = maxPrep;
    if (maxCook) params.max_cook_time = maxCook;
    if (favoriteOnly) params.favorite = true;
    if (ingredient) params.ingredient = ingredient;
    setSearchParams(params);
    setLoading(true);
    client.get('/recipes/', { params }).then((r) => {
      setRecipes(r.data.results || r.data);
      setLoading(false);
    });
  };

  useEffect(() => {
    runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Recettes</h1>
        <Link to="/recipes/new" className="btn-primary">+ Nouvelle recette</Link>
      </div>

      <div className="filter-bar">
        <input
          placeholder="Recherche plein texte (titre, étapes, ingrédients, tags)…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && runSearch()}
          className="search-input"
        />
        <select value={cookbook} onChange={(e) => setCookbook(e.target.value)}>
          <option value="">Tous les cookbooks</option>
          <option value="mine">Mes recettes seules</option>
          {cookbooks.map((cb) => <option key={cb.id} value={cb.id}>{cb.name}</option>)}
        </select>
        <select value={tag} onChange={(e) => setTag(e.target.value)}>
          <option value="">Tous les tags</option>
          {tags.map((t) => <option key={t.id} value={t.name}>{t.name} ({t.category})</option>)}
        </select>
        <input
          placeholder="Ingrédient"
          value={ingredient}
          onChange={(e) => setIngredient(e.target.value)}
          style={{ width: 130 }}
        />
        <input
          type="number"
          placeholder="Prépa max (min)"
          value={maxPrep}
          onChange={(e) => setMaxPrep(e.target.value)}
          style={{ width: 130 }}
        />
        <input
          type="number"
          placeholder="Cuisson max (min)"
          value={maxCook}
          onChange={(e) => setMaxCook(e.target.value)}
          style={{ width: 130 }}
        />
        <label className="checkbox-label">
          <input type="checkbox" checked={favoriteOnly} onChange={(e) => setFavoriteOnly(e.target.checked)} />
          Favoris uniquement
        </label>
        <button className="btn-secondary" onClick={runSearch}>Filtrer</button>
      </div>

      {loading ? (
        <p className="empty">Chargement…</p>
      ) : recipes.length === 0 ? (
        <p className="empty">Aucune recette ne correspond à ces critères.</p>
      ) : (
        <div className="recipe-grid">
          {recipes.map((r) => <RecipeCard key={r.id} recipe={r} />)}
        </div>
      )}
    </div>
  );
}
