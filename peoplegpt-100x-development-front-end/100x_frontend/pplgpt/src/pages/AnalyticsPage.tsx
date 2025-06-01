import { Topbar } from "@/components/Topbar";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";

export default function AnalyticsPage() {
  return (
    <div>
      <Topbar />
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>
        <AnalyticsDashboard />
      </div>
    </div>
  );
}

