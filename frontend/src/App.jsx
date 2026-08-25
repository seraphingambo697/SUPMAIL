import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import { useAuth } from './context/AuthContext.jsx';

import Cookbooks from './pages/Cookbooks.jsx';
import CookbookDetail from './pages/CookbookDetail.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ImportExport from './pages/ImportExport.jsx';
import Login from './pages/Login.jsx';
import OAuthCallback from './pages/OAuthCallback.jsx';
import Planner from './pages/Planner.jsx';
import Recipes from './pages/Recipes.jsx';
import RecipeDetail from './pages/RecipeDetail.jsx';
import RecipeForm from './pages/RecipeForm.jsx';
import Register from './pages/Register.jsx';
import Settings from './pages/Settings.jsx';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center-loader">Chargement…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/oauth/callback/:provider" element={<OAuthCallback />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="recipes" element={<Recipes />} />
        <Route path="recipes/new" element={<RecipeForm />} />
        <Route path="recipes/:id" element={<RecipeDetail />} />
        <Route path="recipes/:id/edit" element={<RecipeForm />} />
        <Route path="cookbooks" element={<Cookbooks />} />
        <Route path="cookbooks/:id" element={<CookbookDetail />} />
        <Route path="planner" element={<Planner />} />
        <Route path="import-export" element={<ImportExport />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
