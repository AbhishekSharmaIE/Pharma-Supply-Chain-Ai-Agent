export default function OrderCard({ decision }) {
  if (!decision) return null;

  return (
    <div className="card">
      <h3>Order {decision.order_id}</h3>
      <p>
        <strong>Priority:</strong> {decision.priority_level}
      </p>
      <p>
        <strong>Reasoning:</strong> {decision.reasoning}
      </p>
      <p>
        <strong>Review:</strong>{" "}
        {decision.requires_human_review
          ? decision.review_reason || "Required"
          : "Not required"}
      </p>
    </div>
  );
}
