import HumanReviewQueue from "../components/HumanReviewQueue";
import OrderCard from "../components/OrderCard";
import OrderTable from "../components/OrderTable";
import SummaryChart from "../components/SummaryChart";
import UploadPanel from "../components/UploadPanel";

export default function Dashboard({
  decisions,
  selectedDecision,
  onSelectDecision,
  onUpload,
}) {
  const totalOrders = decisions.length;
  const criticalCount = decisions.filter((item) => item.priority_level === "CRITICAL").length;
  const reviewCount = decisions.filter((item) => item.requires_human_review).length;
  const avgConfidence =
    totalOrders === 0
      ? 0
      : decisions.reduce((sum, item) => sum + item.confidence_score, 0) / totalOrders;

  return (
    <div className="dashboard-grid">
      <div className="summary-grid">
        <div className="card"><strong>Total Orders:</strong> {totalOrders}</div>
        <div className="card"><strong>Critical:</strong> {criticalCount}</div>
        <div className="card"><strong>Human Review:</strong> {reviewCount}</div>
        <div className="card"><strong>Avg Confidence:</strong> {(avgConfidence * 100).toFixed(1)}%</div>
      </div>

      <UploadPanel onUpload={onUpload} />
      <SummaryChart decisions={decisions} />
      <OrderTable decisions={decisions} onSelect={onSelectDecision} />
      <HumanReviewQueue decisions={decisions} />
      <OrderCard decision={selectedDecision} />
    </div>
  );
}
