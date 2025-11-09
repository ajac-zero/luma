import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Shield,
  Info,
} from "lucide-react";

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

const getSeverityIcon = (severity: Severity, size = "w-4 h-4") => {
  switch (severity) {
    case "Pass":
      return <CheckCircle className={`${size} text-green-600`} />;
    case "Warning":
      return <AlertTriangle className={`${size} text-yellow-600`} />;
    case "Error":
      return <XCircle className={`${size} text-red-600`} />;
    default:
      return <AlertCircle className={`${size} text-gray-600`} />;
  }
};

const getSeverityBadge = (severity: Severity) => {
  const colors = {
    Pass: "bg-green-100 text-green-800 border-green-200",
    Warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    Error: "bg-red-100 text-red-800 border-red-200",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${colors[severity]}`}
    >
      {getSeverityIcon(severity, "w-3 h-3")}
      {severity}
    </span>
  );
};

export const AuditReport: React.FC<AuditReportProps> = ({ data }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(),
  );
  const [showAllFindings, setShowAllFindings] = useState(false);

  const {
    organisation_name,
    organisation_ein,
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

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const criticalFindings = findings.filter((f) => f.severity === "Error");

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Compact Header */}
      <div className="bg-linear-to-r from-blue-50 to-indigo-50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="font-semibold text-gray-900">
                {organisation_name}
              </h3>
              <div className="flex items-center gap-3 text-xs text-gray-600">
                <span>EIN: {organisation_ein}</span>
                {year && <span>{year}</span>}
              </div>
            </div>
          </div>
          {getSeverityBadge(overall_severity)}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            Audit Results
          </span>
          <div className="flex items-center gap-4 text-sm">
            {severityStats.Pass > 0 && (
              <div className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-600" />
                <span className="font-medium text-green-700">
                  {severityStats.Pass}
                </span>
              </div>
            )}
            {severityStats.Warning > 0 && (
              <div className="flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 text-yellow-600" />
                <span className="font-medium text-yellow-700">
                  {severityStats.Warning}
                </span>
              </div>
            )}
            {severityStats.Error > 0 && (
              <div className="flex items-center gap-1">
                <XCircle className="w-3 h-3 text-red-600" />
                <span className="font-medium text-red-700">
                  {severityStats.Error}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Summary */}
        {overall_summary && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
              <div>
                <h4 className="font-medium text-blue-900 text-sm mb-1">
                  Summary
                </h4>
                <p className="text-sm text-blue-800">{overall_summary}</p>
              </div>
            </div>
          </div>
        )}

        {/* Critical Issues (if any) */}
        {criticalFindings.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <h4 className="font-medium text-red-900 text-sm mb-2 flex items-center gap-2">
              <XCircle className="w-4 h-4" />
              Critical Issues ({criticalFindings.length})
            </h4>
            <div className="space-y-2">
              {criticalFindings.slice(0, 2).map((finding, index) => (
                <div key={index} className="text-sm text-red-800">
                  <span className="font-medium">{finding.category}:</span>{" "}
                  {finding.message}
                </div>
              ))}
              {criticalFindings.length > 2 && (
                <button
                  onClick={() => setShowAllFindings(!showAllFindings)}
                  className="text-xs text-red-700 hover:text-red-800 font-medium"
                >
                  {showAllFindings
                    ? "Show less"
                    : `+${criticalFindings.length - 2} more issues`}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Sections Overview */}
        {sections.length > 0 && (
          <div>
            <button
              onClick={() => toggleSection("sections")}
              className="flex items-center gap-2 w-full text-left p-2 hover:bg-gray-50 rounded-lg"
            >
              {expandedSections.has("sections") ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <span className="font-medium text-sm">
                Section Analysis ({sections.length})
              </span>
            </button>

            {expandedSections.has("sections") && (
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {sections.map((section, index) => (
                  <div key={index} className="border rounded-lg p-3 bg-gray-50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">
                        {section.section}
                      </span>
                      <div className="flex items-center gap-1">
                        {getSeverityIcon(section.severity)}
                        <span className="text-xs text-gray-600">
                          {Math.round(section.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-700">{section.summary}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* All Findings */}
        <div>
          <button
            onClick={() => toggleSection("findings")}
            className="flex items-center gap-2 w-full text-left p-2 hover:bg-gray-50 rounded-lg"
          >
            {expandedSections.has("findings") ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <span className="font-medium text-sm">
              All Findings ({findings.length})
            </span>
          </button>

          {expandedSections.has("findings") && (
            <div className="mt-2 space-y-2">
              {findings.map((finding, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(finding.severity)}
                      <div>
                        <span className="font-medium text-sm">
                          {finding.category}
                        </span>
                        <span className="text-xs text-gray-500 ml-1">
                          #{finding.check_id}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs text-gray-600">
                      {Math.round(finding.confidence * 100)}% confidence
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-2">
                    {finding.message}
                  </p>

                  {finding.mitigation && (
                    <div className="bg-white rounded p-2 border">
                      <span className="text-xs font-medium text-gray-600">
                        Recommended:
                      </span>
                      <p className="text-xs text-gray-700 mt-1">
                        {finding.mitigation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notes */}
        {notes && (
          <div className="border-t pt-3">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
              <div>
                <h4 className="font-medium text-gray-700 text-sm mb-1">
                  Notes
                </h4>
                <p className="text-sm text-gray-600 italic">{notes}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
