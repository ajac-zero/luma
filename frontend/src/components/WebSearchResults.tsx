import React, { useState } from "react";
import {
  Globe,
  ExternalLink,
  Search,
  ChevronDown,
  ChevronRight,
  Info,
  Star,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchResult {
  title: string;
  url: string;
  content: string;
  score?: number;
}

interface WebSearchData {
  query: string;
  results: SearchResult[];
  summary: string;
  total_results: number;
}

interface WebSearchResultsProps {
  data: WebSearchData;
}

const getScoreColor = (score?: number) => {
  if (!score) return "text-gray-500";
  if (score >= 0.8) return "text-green-600";
  if (score >= 0.6) return "text-yellow-600";
  return "text-gray-500";
};

const getScoreStars = (score?: number) => {
  if (!score) return 0;
  return Math.round(score * 5);
};

const truncateContent = (content: string, maxLength: number = 200) => {
  if (content.length <= maxLength) return content;
  return content.slice(0, maxLength) + "...";
};

export const WebSearchResults: React.FC<WebSearchResultsProps> = ({ data }) => {
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());
  const [showAllResults, setShowAllResults] = useState(false);

  const { query, results, summary, total_results } = data;

  const toggleResult = (index: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  const visibleResults = showAllResults ? results : results.slice(0, 3);

  return (
    <div className="w-full bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Globe className="w-6 h-6 text-green-600" />
            <div>
              <h3 className="font-semibold text-gray-900">Web Search Results</h3>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Search className="w-3 h-3" />
                <span>"{query}"</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">{results.length}</div>
            <div className="text-xs text-gray-600">
              of {total_results} results
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Summary */}
        {summary && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-medium text-blue-900 text-sm mb-1">
                  Summary
                </h4>
                <p className="text-sm text-blue-800">{summary}</p>
              </div>
            </div>
          </div>
        )}

        {/* Search Results */}
        <div className="space-y-3">
          {visibleResults.map((result, index) => {
            const isExpanded = expandedResults.has(index);
            const stars = getScoreStars(result.score);

            return (
              <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 text-sm mb-1 line-clamp-2">
                        {result.title}
                      </h4>
                      <div className="flex items-center gap-2">
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 truncate"
                        >
                          <ExternalLink className="w-3 h-3 flex-shrink-0" />
                          {new URL(result.url).hostname}
                        </a>
                        {result.score && (
                          <div className="flex items-center gap-1">
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={cn(
                                    "w-3 h-3",
                                    i < stars
                                      ? "text-yellow-400 fill-current"
                                      : "text-gray-300"
                                  )}
                                />
                              ))}
                            </div>
                            <span className={cn("text-xs font-medium", getScoreColor(result.score))}>
                              {Math.round((result.score || 0) * 100)}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="text-sm text-gray-700">
                    {isExpanded ? result.content : truncateContent(result.content)}
                  </div>

                  {result.content.length > 200 && (
                    <button
                      onClick={() => toggleResult(index)}
                      className="mt-2 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronDown className="w-3 h-3" />
                          Show less
                        </>
                      ) : (
                        <>
                          <ChevronRight className="w-3 h-3" />
                          Read more
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Show More/Less Button */}
        {results.length > 3 && (
          <div className="text-center">
            <button
              onClick={() => setShowAllResults(!showAllResults)}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors"
            >
              {showAllResults
                ? "Show fewer results"
                : `Show ${results.length - 3} more results`}
            </button>
          </div>
        )}

        {/* No Results */}
        {results.length === 0 && (
          <div className="text-center py-6">
            <Search className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">No results found for "{query}"</p>
          </div>
        )}
      </div>
    </div>
  );
};
