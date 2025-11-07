import { useState, useEffect } from "react";
import {
  FileText,
  Database,
  Activity,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader2,
} from "lucide-react";
import { api } from "@/services/api";

interface DashboardTabProps {
  selectedTema: string | null;
}

interface DataroomInfo {
  name: string;
  collection: string;
  storage: string;
  file_count: number;
  total_size_bytes: number;
  total_size_mb: number;
  collection_exists: boolean;
  vector_count: number | null;
  collection_info: {
    vectors_count: number;
    indexed_vectors_count: number;
    points_count: number;
    segments_count: number;
    status: string;
  } | null;
  file_types: Record<string, number>;
  recent_files: Array<{
    name: string;
    size_mb: number;
    last_modified: string;
  }>;
}

export function DashboardTab({ selectedTema }: DashboardTabProps) {
  const [dataroomInfo, setDataroomInfo] = useState<DataroomInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedTema) {
      fetchDataroomInfo();
    }
  }, [selectedTema]);

  const fetchDataroomInfo = async () => {
    if (!selectedTema) return;

    setLoading(true);
    setError(null);

    try {
      const info = await api.getDataroomInfo(selectedTema);
      setDataroomInfo(info);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Error desconocido";
      setError(`Error cargando información: ${errorMessage}`);
      console.error("Error fetching dataroom info:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatFileTypes = (fileTypes: Record<string, number>) => {
    const entries = Object.entries(fileTypes);
    if (entries.length === 0) return "Sin archivos";

    return entries
      .sort(([, a], [, b]) => b - a) // Sort by count descending
      .slice(0, 3) // Take top 3
      .map(([ext, count]) => `${ext.toUpperCase()}: ${count}`)
      .join(", ");
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 MB";
    const mb = bytes / (1024 * 1024);
    if (mb < 1) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${mb.toFixed(1)} MB`;
  };

  if (!selectedTema) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Activity className="w-12 h-12 text-gray-400 mb-4" />
        <p className="text-gray-500">
          Selecciona un dataroom para ver las métricas
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-600">Cargando métricas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dataroomInfo) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <AlertCircle className="w-12 h-12 text-gray-400 mb-4" />
        <p className="text-gray-500">
          No se pudo cargar la información del dataroom
        </p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Métricas del Dataroom: {selectedTema}
        </h3>
        <p className="text-sm text-gray-600">
          Vista general del estado y actividad del dataroom
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Files Count Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Archivos</p>
              <p className="text-2xl font-bold text-gray-900">
                {dataroomInfo.file_count}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatFileTypes(dataroomInfo.file_types)}
              </p>
            </div>
          </div>
        </div>

        {/* Storage Usage Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Database className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">
                Almacenamiento
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {dataroomInfo.total_size_mb.toFixed(1)} MB
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatBytes(dataroomInfo.total_size_bytes)}
              </p>
            </div>
          </div>
        </div>

        {/* Vector Collections Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Vectores</p>
              <p className="text-2xl font-bold text-gray-900">
                {dataroomInfo.vector_count ?? 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {dataroomInfo.collection_exists
                  ? "Vectores indexados"
                  : "Sin vectores"}
              </p>
            </div>
          </div>
        </div>

        {/* Collection Status Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Estado</p>
              <div className="flex items-center gap-2">
                <p className="text-2xl font-bold text-gray-900">
                  {dataroomInfo.collection_exists ? "Activo" : "Inactivo"}
                </p>
                {dataroomInfo.collection_exists ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-yellow-600" />
                )}
              </div>
              {dataroomInfo.collection_info ? (
                <p className="text-xs text-gray-500 mt-1">
                  {dataroomInfo.collection_info.indexed_vectors_count}/
                  {dataroomInfo.collection_info.vectors_count} vectores
                  indexados
                </p>
              ) : (
                <p className="text-xs text-gray-500 mt-1">
                  {dataroomInfo.collection_exists
                    ? "Colección sin datos"
                    : "Sin colección"}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Files Section */}
      {dataroomInfo.recent_files.length > 0 && (
        <div className="mt-8">
          <h4 className="text-md font-semibold text-gray-900 mb-4">
            Archivos Recientes
          </h4>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="divide-y divide-gray-200">
              {dataroomInfo.recent_files.map((file, index) => (
                <div
                  key={index}
                  className="p-4 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(file.last_modified).toLocaleDateString(
                          "es-ES",
                          {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {file.size_mb.toFixed(2)} MB
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Collection Details */}
      {dataroomInfo.collection_info && (
        <div className="mt-8">
          <h4 className="text-md font-semibold text-gray-900 mb-4">
            Detalles de la Colección
          </h4>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Vectores
                </p>
                <p className="text-lg font-bold text-gray-900">
                  {dataroomInfo.collection_info.vectors_count}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Vectores Indexados
                </p>
                <p className="text-lg font-bold text-gray-900">
                  {dataroomInfo.collection_info.indexed_vectors_count}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Puntos</p>
                <p className="text-lg font-bold text-gray-900">
                  {dataroomInfo.collection_info.points_count}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Segmentos</p>
                <p className="text-lg font-bold text-gray-900">
                  {dataroomInfo.collection_info.segments_count}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
