import { useMemo, useState } from "react";
import { uploadCSV } from "./api/agentApi";
import AuditLog from "./pages/AuditLog";
import Dashboard from "./pages/Dashboard";

const AUDIT_KEY = "pharma_agent_audit_log";

function getStoredRuns() {
  try {
    const raw = localStorage.getItem(AUDIT_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [latestBatch, setLatestBatch] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [runs, setRuns] = useState(getStoredRuns);

  async function handleUpload(file) {
    const result = await uploadCSV(file);
    setLatestBatch(result);
    setSelectedDecision(result.decisions?.[0] || null);

    const newRun = {
      ...result,
      timestamp: new Date().toISOString(),
    };
    const updatedRuns = [newRun, ...runs].slice(0, 100);
    setRuns(updatedRuns);
    localStorage.setItem(AUDIT_KEY, JSON.stringify(updatedRuns));
  }

  const decisions = useMemo(() => latestBatch?.decisions || [], [latestBatch]);

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Pharma Agent</h1>
        <button className="btn nav-btn" onClick={() => setActivePage("dashboard")}>
          Dashboard
        </button>
        <button className="btn nav-btn" onClick={() => setActivePage("audit")}>
          Audit Log
        </button>
      </aside>

      <main className="content">
        <header className="header">
          <h2>Pharma Supply Chain AI Agent</h2>
        </header>

        {activePage === "dashboard" ? (
          <Dashboard
            decisions={decisions}
            selectedDecision={selectedDecision}
            onSelectDecision={setSelectedDecision}
            onUpload={handleUpload}
          />
        ) : (
          <AuditLog runs={runs} />
        )}
      </main>
    </div>
  );
}
