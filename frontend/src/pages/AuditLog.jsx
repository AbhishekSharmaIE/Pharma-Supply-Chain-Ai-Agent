export default function AuditLog({ runs }) {
  return (
    <div className="card">
      <h2>Audit Log</h2>
      {runs.length === 0 ? (
        <p className="muted">No batch runs yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Batch ID</th>
              <th>Timestamp</th>
              <th>Total Orders</th>
              <th>Human Reviews</th>
              <th>Processing Time</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={`${run.batch_id}-${run.timestamp}`}>
                <td>{run.batch_id}</td>
                <td>{run.timestamp}</td>
                <td>{run.total_orders}</td>
                <td>{run.human_review_count}</td>
                <td>{run.processing_time_seconds.toFixed(2)}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
