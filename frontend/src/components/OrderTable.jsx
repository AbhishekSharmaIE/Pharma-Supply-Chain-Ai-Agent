import { useMemo, useState } from "react";
import ConfidenceGauge from "./ConfidenceGauge";

const PRIORITY_CLASS = {
  CRITICAL: "badge critical",
  HIGH: "badge high",
  MEDIUM: "badge medium",
  LOW: "badge low",
};

export default function OrderTable({ decisions, onSelect }) {
  const [sortField, setSortField] = useState("order_id");
  const [sortDirection, setSortDirection] = useState("asc");

  const sorted = useMemo(() => {
    const rows = [...decisions];
    rows.sort((a, b) => {
      const av = a[sortField];
      const bv = b[sortField];
      const result = av > bv ? 1 : av < bv ? -1 : 0;
      return sortDirection === "asc" ? result : -result;
    });
    return rows;
  }, [decisions, sortDirection, sortField]);

  function toggleSort(field) {
    if (field === sortField) {
      setSortDirection((dir) => (dir === "asc" ? "desc" : "asc"));
      return;
    }
    setSortField(field);
    setSortDirection("asc");
  }

  return (
    <div className="card">
      <h3>Order Decisions</h3>
      <table className="table">
        <thead>
          <tr>
            <th onClick={() => toggleSort("order_id")}>Order ID</th>
            <th onClick={() => toggleSort("priority_level")}>Priority</th>
            <th onClick={() => toggleSort("confidence_score")}>Confidence</th>
            <th>Review Flag</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((item) => (
            <tr key={item.order_id}>
              <td>{item.order_id}</td>
              <td>
                <span className={PRIORITY_CLASS[item.priority_level] || "badge"}>
                  {item.priority_level}
                </span>
              </td>
              <td>
                <ConfidenceGauge score={item.confidence_score} />
              </td>
              <td>{item.requires_human_review ? "Yes" : "No"}</td>
              <td>
                <button className="btn" onClick={() => onSelect(item)}>
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
