import { useState } from "react";

export default function UploadPanel({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a CSV file.");
      return;
    }

    setError("");
    setLoading(true);
    try {
      await onUpload(file);
      setFile(null);
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>Upload CSV</h3>
      <p className="muted">Drop or select a batch file for prioritization.</p>
      <input
        type="file"
        accept=".csv"
        onChange={(event) => setFile(event.target.files?.[0] || null)}
      />
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? "Processing..." : "Upload CSV"}
      </button>
      {error ? <p className="error">{error}</p> : null}
    </form>
  );
}
