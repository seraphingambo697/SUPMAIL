import { useEffect, useState } from 'react';
import client from '../api/client';

const MEAL_TYPES = [
  { value: 'breakfast', label: 'Petit-déjeuner' },
  { value: 'lunch', label: 'Déjeuner' },
  { value: 'dinner', label: 'Dîner' },
  { value: 'snack', label: 'Collation' },
];

function startOfWeek(date) {
  const d = new Date(date);
  const day = (d.getDay() + 6) % 7; // lundi = 0
  d.setDate(d.getDate() - day);
  d.setHours(0, 0, 0, 0);
  return d;
}

function fmt(date) {
  return date.toISOString().slice(0, 10);
}

export default function Planner() {
  const [weekStart, setWeekStart] = useState(startOfWeek(new Date()));
  const [plans, setPlans] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [shoppingList, setShoppingList] = useState(null);
  const [selectedRecipe, setSelectedRecipe] = useState('');
  const [selectedDate, setSelectedDate] = useState(fmt(new Date()));
  const [selectedMeal, setSelectedMeal] = useState('dinner');

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + i);
    return d;
  });

  const loadPlans = () => {
    client
      .get('/meal-plans/', { params: { date__gte: fmt(days[0]), date__lte: fmt(days[6]) } })
      .then((r) => setPlans(r.data.results || r.data));
  };

  useEffect(() => {
    client.get('/recipes/').then((r) => setRecipes(r.data.results || r.data));
  }, []);

  useEffect(() => {
    loadPlans();
    setShoppingList(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekStart]);

  const addPlan = async (e) => {
    e.preventDefault();
    if (!selectedRecipe) return;
    await client.post('/meal-plans/', { recipe: selectedRecipe, date: selectedDate, meal_type: selectedMeal });
    loadPlans();
  };

  const removePlan = async (planId) => {
    await client.delete(`/meal-plans/${planId}/`);
    loadPlans();
  };

  const generateShoppingList = async () => {
    const { data } = await client.get('/meal-plans/shopping_list/', {
      params: { start: fmt(days[0]), end: fmt(days[6]) },
    });
    setShoppingList(data);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Planning de repas</h1>
        <div className="btn-row">
          <button className="btn-ghost" onClick={() => setWeekStart((d) => { const nd = new Date(d); nd.setDate(nd.getDate() - 7); return nd; })}>← Semaine préc.</button>
          <button className="btn-ghost" onClick={() => setWeekStart(startOfWeek(new Date()))}>Aujourd'hui</button>
          <button className="btn-ghost" onClick={() => setWeekStart((d) => { const nd = new Date(d); nd.setDate(nd.getDate() + 7); return nd; })}>Semaine suiv. →</button>
        </div>
      </div>

      <form onSubmit={addPlan} className="inline-form">
        <select value={selectedRecipe} onChange={(e) => setSelectedRecipe(e.target.value)} required>
          <option value="">Choisir une recette…</option>
          {recipes.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
        </select>
        <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
        <select value={selectedMeal} onChange={(e) => setSelectedMeal(e.target.value)}>
          {MEAL_TYPES.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
        </select>
        <button className="btn-primary" type="submit">Ajouter au planning</button>
      </form>

      <div className="planner-grid">
        {days.map((day) => {
          const dayStr = fmt(day);
          const dayPlans = plans.filter((p) => p.date === dayStr);
          return (
            <div key={dayStr} className="planner-day">
              <h3>{day.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })}</h3>
              {dayPlans.length === 0 && <p className="empty small">Rien de prévu</p>}
              {dayPlans.map((p) => (
                <div key={p.id} className="planner-entry">
                  <span className="meal-type-tag">{MEAL_TYPES.find((m) => m.value === p.meal_type)?.label}</span>
                  <strong>{p.recipe_detail?.title}</strong>
                  <button className="btn-ghost small" onClick={() => removePlan(p.id)}>✕</button>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      <section className="section">
        <div className="section-header">
          <h2>Liste de courses</h2>
          <button className="btn-secondary" onClick={generateShoppingList}>Générer pour cette semaine</button>
        </div>
        {shoppingList && (
          shoppingList.length === 0 ? (
            <p className="empty">Aucun ingrédient à prévoir cette semaine.</p>
          ) : (
            <ul className="shopping-list">
              {shoppingList.map((item, idx) => (
                <li key={idx}>{item.quantity} {item.unit} — {item.ingredient}</li>
              ))}
            </ul>
          )
        )}
      </section>
    </div>
  );
}
