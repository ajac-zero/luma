import React from "react";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  FileText,
  Building,
  Calendar,
  AlertCircle,
  TrendingUp,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";

type Severity = "Pass" | "Warning" | "Error";

interface AuditFinding {
  check_id: string;
  category: string;
  severity: Severity;
  message: string;
  mitigation?: string;
  confidence: number;
}

interface AuditSectionSummary {
  section: string;
  severity: Severity;
  summary: string;
  confidence: number;
}

interface AuditReportData {
  organisation_ein: string;
  organisation_name: string;
  year?: number;
  overall_severity: Severity;
  findings: AuditFinding[];
  sections: AuditSectionSummary[];
  overall_summary?: string;
  notes?: string;
}

interface AuditReportProps {
  data: AuditReportData;
}

const getSeverityIcon = (severity: Severity) => {
  switch (severity) {
    case "Pass":
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    case "Warning":
      return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    case "Error":
      return <XCircle className="w-5 h-5 text-red-600" />;
    default:
      return <AlertCircle className="w-5 h-5 text-gray-600" />;
  }
};

const getSeverityColor = (severity: Severity) => {
  switch (severity) {
    case "Pass":
      return "text-green-700 bg-green-50 border-green-200";
    case "Warning":
      return "text-yellow-700 bg-yellow-50 border-yellow-200";
    case "Error":
      return "text-red-700 bg-red-50 border-red-200";
    default:
      return "text-gray-700 bg-gray-50 border-gray-200";
  }
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return "text-green-600";
  if (confidence >= 0.6) return "text-yellow-600";
  return "text-red-600";
};

export const AuditReport: React.FC<AuditReportProps> = ({ data }) => {
  const {
    organisation_ein,
    organisation_name,
    year,
    overall_severity,
    findings,
    sections,
    overall_summary,
    notes,
  } = data;

  const severityStats = {
    Pass: findings.filter((f) => f.severity === "Pass").length,
    Warning: findings.filter((f) => f.severity === "Warning").length,
    Error: findings.filter((f) => f.severity === "Error").length,
  };

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div>
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 p-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <Building className="w-5 h-5" />
                  {organisation_name}
                </h2>
                <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    EIN: {organisation_ein}
                  </span>
                  {year && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {year}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Overall Status */}
            <div
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full border",
                getSeverityColor(overall_severity),
              )}
            >
              {getSeverityIcon(overall_severity)}
              <span className="font-medium">{overall_severity}</span>
            </div>
          </div>
        </div>

        {/* Statistics Bar */}
        <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">Audit Summary</h3>
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-green-700 font-medium">
                  {severityStats.Pass}
                </span>
                <span className="text-gray-600">Passed</span>
              </div>
              <div className="flex items-center gap-1">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <span className="text-yellow-700 font-medium">
                  {severityStats.Warning}
                </span>
                <span className="text-gray-600">Warnings</span>
              </div>
              <div className="flex items-center gap-1">
                <XCircle className="w-4 h-4 text-red-600" />
                <span className="text-red-700 font-medium">
                  {severityStats.Error}
                </span>
                <span className="text-gray-600">Errors</span>
              </div>
            </div>
          </div>
        </div>

        {/* Overall Summary */}
        {overall_summary && (
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-3">
              Overall Assessment
            </h3>
            <p className="text-gray-700 leading-relaxed">{overall_summary}</p>
          </div>
        )}

        {/* Section Summaries */}
        {sections.length > 0 && (
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Section Analysis
            </h3>
            <div className="grid gap-2 sm:grid-cols-2">
              {sections.map((section, index) => (
                <div
                  key={index}
                  className={cn(
                    "border rounded-lg p-3",
                    getSeverityColor(section.severity),
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{section.section}</h4>
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(section.severity)}
                      <span
                        className={cn(
                          "text-xs font-medium",
                          getConfidenceColor(section.confidence),
                        )}
                      >
                        {Math.round(section.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm opacity-90">{section.summary}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Findings */}
        <div className="p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Detailed Findings ({findings.length})
          </h3>
          <div className="space-y-3">
            {findings.map((finding, index) => (
              <div
                key={index}
                className={cn(
                  "border rounded-lg p-3",
                  getSeverityColor(finding.severity),
                )}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {getSeverityIcon(finding.severity)}
                    <div>
                      <span className="font-medium">{finding.category}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        #{finding.check_id}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                    <span
                      className={cn(
                        "text-sm font-medium",
                        getConfidenceColor(finding.confidence),
                      )}
                    >
                      {Math.round(finding.confidence * 100)}% confidence
                    </span>
                  </div>
                </div>

                <p className="text-sm mb-2 leading-relaxed">
                  {finding.message}
                </p>

                {finding.mitigation && (
                  <div className="bg-white bg-opacity-50 rounded p-2 border border-current border-opacity-20">
                    <h5 className="font-medium text-sm mb-1">
                      Recommended Action:
                    </h5>
                    <p className="text-sm">{finding.mitigation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Notes */}
        {notes && (
          <div className="bg-gray-50 p-3 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">
              Additional Notes
            </h3>
            <p className="text-sm text-gray-600 italic">{notes}</p>
          </div>
        )}
      </div>
    </div>
  );
};
