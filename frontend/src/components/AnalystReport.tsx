import {
  TrendingUp,
  TrendingDown,
  Activity,
  Info,
  Target,
  Lightbulb,
  ArrowRight,
  AlertTriangle,
} from "lucide-react";

type TrendDirection = "Improving" | "Declining" | "Stable" | "Volatile";

interface TrendMetricPoint {
  year: number;
  value: number;
  growth?: number | null;
}

interface TrendMetric {
  name: string;
  unit: string;
  description: string;
  points: TrendMetricPoint[];
  cagr?: number | null;
  direction: TrendDirection;
  notes?: string | null;
}

interface TrendInsight {
  category: string;
  direction: TrendDirection;
  summary: string;
  confidence: number;
}

interface AnalystReportData {
  organisation_name: string;
  organisation_ein: string;
  years_analyzed: number[];
  key_metrics: TrendMetric[];
  insights: TrendInsight[];
  recommendations: string[];
  outlook: string;
}

interface AnalystReportProps {
  data: AnalystReportData;
}

const directionBadgeClasses: Record<TrendDirection, string> = {
  Improving: "bg-green-100 text-green-700 border-green-200",
  Declining: "bg-red-100 text-red-700 border-red-200",
  Stable: "bg-blue-100 text-blue-700 border-blue-200",
  Volatile: "bg-yellow-100 text-yellow-700 border-yellow-200",
};

const directionIcon = (direction: TrendDirection) => {
  switch (direction) {
    case "Improving":
      return <TrendingUp className="w-4 h-4" />;
    case "Declining":
      return <TrendingDown className="w-4 h-4" />;
    case "Volatile":
      return <Activity className="w-4 h-4" />;
    default:
      return <Info className="w-4 h-4" />;
  }
};

const formatNumber = (value: number, unit: string) => {
  if (unit === "USD") {
    return `$${value.toLocaleString("en-US", {
      maximumFractionDigits: 0,
    })}`;
  }
  if (unit === "Ratio") {
    return `${(value * 100).toFixed(1)}%`;
  }
  return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
};

const formatPercent = (value?: number | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "—";
  }
  return `${(value * 100).toFixed(1)}%`;
};

export function AnalystReport({ data }: AnalystReportProps) {
  const {
    organisation_name,
    organisation_ein,
    years_analyzed,
    key_metrics,
    insights,
    recommendations,
    outlook,
  } = data;

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div className="bg-gradient-to-r from-emerald-50 to-sky-50 px-4 py-3 border-b border-emerald-100">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Multi-year performance analysis
            </p>
            <h3 className="text-lg font-semibold text-gray-900">
              {organisation_name}
            </h3>
            <p className="text-xs text-gray-600">
              EIN {organisation_ein} • {years_analyzed.join(" – ")}
            </p>
          </div>
          <div className="text-right text-sm text-gray-600">
            <span className="font-medium text-gray-900">Outlook</span>
            <p className="text-xs text-gray-600 max-w-xs">{outlook}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      {key_metrics.length > 0 && (
        <div className="p-4 space-y-3">
          <h4 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            Core Trend Metrics
          </h4>
          <div className="grid gap-3 md:grid-cols-2">
            {key_metrics.slice(0, 4).map((metric, index) => {
              const latest = metric.points[metric.points.length - 1];
              const prior =
                metric.points.length > 1
                  ? metric.points[metric.points.length - 2]
                  : null;
              const yoy = latest && prior ? formatPercent(latest.growth) : "—";
              return (
                <div
                  key={`${metric.name}-${index}`}
                  className="border rounded-lg p-3 bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-medium text-sm text-gray-900">
                      {metric.name}
                    </div>
                    <span
                      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border ${directionBadgeClasses[metric.direction]}`}
                    >
                      {directionIcon(metric.direction)}
                      {metric.direction}
                    </span>
                  </div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {latest ? formatNumber(latest.value, metric.unit) : "—"}
                  </p>
                  <div className="flex justify-between text-xs text-gray-600 mt-1">
                    <span>YoY: {yoy}</span>
                    <span>CAGR: {formatPercent(metric.cagr)}</span>
                  </div>
                  {metric.notes && (
                    <p className="text-xs text-gray-500 mt-2">{metric.notes}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="px-4 pb-4">
          <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-500" />
            Key Insights
          </h4>
          <div className="space-y-2">
            {insights.map((insight, index) => (
              <div
                key={`${insight.category}-${index}`}
                className="border rounded-lg p-3 bg-white"
              >
                <div className="flex justify-between items-center mb-1">
                  <div className="flex items-center gap-2 text-sm font-medium text-gray-900">
                    {directionIcon(insight.direction)}
                    {insight.category}
                  </div>
                  <span className="text-xs text-gray-500">
                    {Math.round(insight.confidence * 100)}% confidence
                  </span>
                </div>
                <p className="text-sm text-gray-700">{insight.summary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="px-4 pb-4">
          <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <Target className="w-4 h-4 text-indigo-500" />
            Recommended Actions
          </h4>
          <ul className="space-y-1 text-sm text-gray-700">
            {recommendations.map((rec, index) => (
              <li
                key={`rec-${index}`}
                className="flex items-start gap-2 bg-gray-50 border border-gray-100 rounded-lg p-2"
              >
                <ArrowRight className="w-4 h-4 text-gray-500 mt-0.5" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Empty states fallback */}
      {recommendations.length === 0 && insights.length === 0 && (
        <div className="px-4 py-6 text-sm text-gray-600 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-gray-400" />
          No trend insights available yet. Try requesting an annual comparison.
        </div>
      )}
    </div>
  );
}
