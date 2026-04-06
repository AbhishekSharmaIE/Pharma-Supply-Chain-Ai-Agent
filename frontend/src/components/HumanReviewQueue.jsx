import { useMemo, useState } from "react";

export default function HumanReviewQueue({ decisions }) {
  const [resolved, setResolved] = useState({});
  const queue = useMemo(
    () => decisions.filter((item) => item.requires_human_review && !resolved[item.order_id]),
    [decisions, resolved]
  );

  return (
    <div className="card">
      <h3>Human Review Queue</h3>
      {queue.length === 0 ? (
        <p className="muted">No orders pending review.</p>
      ) : (
        queue.map((item) => (
          <div className="review-item" key={item.order_id}>
            <div>
              <strong>{item.order_id}</strong>
              <p className="muted">{item.review_reason || "Manual review required."}</p>
            </div>
            <button
              className="btn"
              onClick={() => setResolved((current) => ({ ...current, [item.order_id]: true }))}
            >
              Mark Resolved
            </button>
          </div>
        ))
      )}
    </div>
  );
}
