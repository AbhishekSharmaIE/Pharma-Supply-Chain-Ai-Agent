export default function ConfidenceGauge({ score }) {
  const pct = Math.max(0, Math.min(1, Number(score || 0)));
  const angle = -90 + pct * 180;
  const color = pct >= 0.85 ? "#16a34a" : pct >= 0.75 ? "#f59e0b" : "#dc2626";

  return (
    <div className="gauge">
      <svg viewBox="0 0 120 70" width="120" height="70">
        <path d="M10 60 A50 50 0 0 1 110 60" stroke="#d1d5db" strokeWidth="10" fill="none" />
        <line
          x1="60"
          y1="60"
          x2={60 + 45 * Math.cos((angle * Math.PI) / 180)}
          y2={60 + 45 * Math.sin((angle * Math.PI) / 180)}
          stroke={color}
          strokeWidth="4"
        />
        <circle cx="60" cy="60" r="4" fill={color} />
      </svg>
      <span>{(pct * 100).toFixed(0)}%</span>
    </div>
  );
}
