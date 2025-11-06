import { FileText, Users, Database, Activity } from "lucide-react";

interface DashboardTabProps {
  selectedTema: string | null;
}

export function DashboardTab({ selectedTema }: DashboardTabProps) {
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
              <p className="text-2xl font-bold text-gray-900">--</p>
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
              <p className="text-sm font-medium text-gray-600">Almacenamiento</p>
              <p className="text-2xl font-bold text-gray-900">--</p>
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
              <p className="text-2xl font-bold text-gray-900">--</p>
            </div>
          </div>
        </div>

        {/* Activity Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Users className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Actividad</p>
              <p className="text-2xl font-bold text-gray-900">--</p>
            </div>
          </div>
        </div>
      </div>

      {/* Coming Soon Message */}
      <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="text-center">
          <Activity className="w-8 h-8 text-gray-400 mx-auto mb-3" />
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Panel de Métricas
          </h4>
          <p className="text-sm text-gray-500">
            Este panel se llenará con métricas detalladas y gráficos interactivos próximamente.
          </p>
        </div>
      </div>
    </div>
  );
}
