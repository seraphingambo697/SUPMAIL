import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import client from '../api/client';

const emptyIngredient = () => ({ ingredient_name: '', quantity: 1, unit: '' });

export default function RecipeForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [steps, setSteps] = useState('');
  const [prepTime, setPrepTime] = useState(15);
  const [cookTime, setCookTime] = useState(15);
  const [servings, setServings] = useState(4);
  const [source, setSource] = useState('');
  const [cookbookId, setCookbookId] = useState('');
  const [ingredients, setIngredients] = useState([emptyIngredient()]);
  const [tagIds, setTagIds] = useState([]);
  const [imageFile, setImageFile] = useState(null);
  const [cookbooks, setCookbooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    client.get('/cookbooks/').then((r) => setCookbooks(r.data.results || r.data));
    client.get('/tags/').then((r) => setTags(r.data.results || r.data));
    if (isEdit) {
      client.get(`/recipes/${id}/`).then((r) => {
        const rec = r.data;
        setTitle(rec.title);
        setSteps(rec.steps);
        setPrepTime(rec.prep_time_minutes);
        setCookTime(rec.cook_time_minutes);
        setServings(rec.servings);
        setSource(rec.source || '');
        setCookbookId(rec.cookbook || '');
        setIngredients(
          rec.ingredients.map((i) => ({
            ingredient_name: i.ingredient.name, quantity: i.quantity, unit: i.unit,
          }))
        );
        setTagIds(rec.tags.map((t) => t.id));
      });
    }
  }, [id]);

  const updateIngredient = (idx, field, value) => {
    const copy = [...ingredients];
    copy[idx] = { ...copy[idx], [field]: value };
    setIngredients(copy);
  };

  const addIngredientRow = () => setIngredients([...ingredients, emptyIngredient()]);
  const removeIngredientRow = (idx) => setIngredients(ingredients.filter((_, i) => i !== idx));

  const toggleTag = (tagId) => {
    setTagIds((prev) => (prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId]));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const payload = {
        title, steps,
        prep_time_minutes: Number(prepTime),
        cook_time_minutes: Number(cookTime),
        servings: Number(servings),
        source,
        cookbook: cookbookId || null,
        tag_ids: tagIds,
        ingredients: ingredients
          .filter((i) => i.ingredient_name.trim())
          .map((i) => ({ ingredient_name: i.ingredient_name, quantity: Number(i.quantity), unit: i.unit })),
      };

      let recipeId = id;
      if (isEdit) {
        await client.patch(`/recipes/${id}/`, payload);
      } else {
        const { data } = await client.post('/recipes/', payload);
        recipeId = data.id;
      }

      if (imageFile) {
        const form = new FormData();
        form.append('image', imageFile);
        await client.patch(`/recipes/${recipeId}/`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
      }

      navigate(`/recipes/${recipeId}`);
    } catch (err) {
      setError("Erreur lors de l'enregistrement. Vérifiez les champs.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page">
      <h1>{isEdit ? 'Modifier la recette' : 'Nouvelle recette'}</h1>
      <form onSubmit={handleSubmit} className="form recipe-form">
        <label>Titre *</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />

        <div className="form-row">
          <div>
            <label>Temps de préparation (min)</label>
            <input type="number" min="0" value={prepTime} onChange={(e) => setPrepTime(e.target.value)} />
          </div>
          <div>
            <label>Temps de cuisson (min)</label>
            <input type="number" min="0" value={cookTime} onChange={(e) => setCookTime(e.target.value)} />
          </div>
          <div>
            <label>Portions</label>
            <input type="number" min="1" value={servings} onChange={(e) => setServings(e.target.value)} />
          </div>
        </div>

        <label>Cookbook (optionnel — sinon recette personnelle)</label>
        <select value={cookbookId} onChange={(e) => setCookbookId(e.target.value)}>
          <option value="">Recette personnelle</option>
          {cookbooks.map((cb) => <option key={cb.id} value={cb.id}>{cb.name}</option>)}
        </select>

        <label>Source (URL ou "Création personnelle")</label>
        <input value={source} onChange={(e) => setSource(e.target.value)} />

        <label>Image</label>
        <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />

        <label>Tags</label>
        <div className="tag-selector">
          {tags.map((t) => (
            <button
              type="button"
              key={t.id}
              className={`tag-pill selectable ${tagIds.includes(t.id) ? 'selected' : ''}`}
              onClick={() => toggleTag(t.id)}
            >
              {t.name}
            </button>
          ))}
        </div>

        <label>Ingrédients</label>
        {ingredients.map((ing, idx) => (
          <div key={idx} className="ingredient-row">
            <input
              placeholder="Ingrédient"
              value={ing.ingredient_name}
              onChange={(e) => updateIngredient(idx, 'ingredient_name', e.target.value)}
            />
            <input
              type="number"
              placeholder="Qté"
              value={ing.quantity}
              onChange={(e) => updateIngredient(idx, 'quantity', e.target.value)}
              style={{ width: 80 }}
            />
            <input
              placeholder="Unité (g, ml, pièce…)"
              value={ing.unit}
              onChange={(e) => updateIngredient(idx, 'unit', e.target.value)}
              style={{ width: 130 }}
            />
            <button type="button" className="btn-ghost" onClick={() => removeIngredientRow(idx)}>✕</button>
          </div>
        ))}
        <button type="button" className="btn-secondary" onClick={addIngredientRow}>+ Ajouter un ingrédient</button>

        <label>Étapes (une par ligne) *</label>
        <textarea rows={8} value={steps} onChange={(e) => setSteps(e.target.value)} required />

        {error && <p className="error-text">{error}</p>}
        <button className="btn-primary" type="submit" disabled={saving}>
          {saving ? 'Enregistrement…' : (isEdit ? 'Enregistrer' : 'Créer la recette')}
        </button>
      </form>
    </div>
  );
}
