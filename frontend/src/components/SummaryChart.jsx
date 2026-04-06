import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = {
  CRITICAL: "#dc2626",
  HIGH: "#f59e0b",
  MEDIUM: "#2563eb",
  LOW: "#6b7280",
};

export default function SummaryChart({ decisions }) {
  const counts = decisions.reduce(
    (acc, item) => {
      acc[item.priority_level] = (acc[item.priority_level] || 0) + 1;
      return acc;
    },
    { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }
  );

  const data = Object.entries(counts).map(([name, value]) => ({ name, value }));

  return (
    <div className="card chart-card">
      <h3>Priority Distribution</h3>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={90} label>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || "#9ca3af"} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
