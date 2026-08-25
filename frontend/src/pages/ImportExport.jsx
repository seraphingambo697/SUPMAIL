import { useState } from 'react';
import client from '../api/client';

export default function ImportExport() {
  const [format, setFormat] = useState('json');
  const [file, setFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [error, setError] = useState('');
  const [confirmed, setConfirmed] = useState(false);

  const handleExport = async () => {
    const response = await client.get('/export/', { params: { export_format: format }, responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `supmeal_export.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError('');
    setImportResult(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await client.post('/import/', form, { headers: { 'Content-Type': 'multipart/form-data' } });
      setImportResult(data);
    } catch (err) {
      setError("Échec de l'import. Vérifiez le format du fichier.");
    }
  };

  return (
    <div className="page">
      <h1>Import / Export</h1>

      <section className="section card">
        <h2>Exporter mes données</h2>
        <p className="subtitle">
          ⚠️ L'export contient l'ensemble de vos recettes et cookbooks en clair (JSON ou CSV, format compatible Mealie).
          Conservez ce fichier en lieu sûr.
        </p>
        <div className="inline-form">
          <select value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="json">JSON (compatible Mealie)</option>
            <option value="csv">CSV</option>
          </select>
          <button className="btn-primary" onClick={handleExport}>Télécharger l'export</button>
        </div>
      </section>

      <section className="section card">
        <h2>Importer des recettes</h2>
        <p className="subtitle">Formats acceptés : JSON (SUPMEAL/Mealie) ou CSV. Vous serez défini comme créateur des éléments importés.</p>
        <form onSubmit={handleImport} className="inline-form">
          <input type="file" accept=".json,.csv" onChange={(e) => setFile(e.target.files[0])} />
          <button className="btn-primary" type="submit" disabled={!file}>Importer</button>
        </form>
        {importResult && (
          <p className="success-text">
            Import réussi : {importResult.recipes_created} recette(s), {importResult.cookbooks_created} cookbook(s) créé(s).
          </p>
        )}
        {error && <p className="error-text">{error}</p>}
      </section>
    </div>
  );
}
