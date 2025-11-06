import { useEffect, useState, type ReactElement } from "react";
import { useFileStore } from "@/stores/fileStore";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import {
  FolderIcon,
  FileText,
  Trash2,
  Database,
  ChevronLeft,
  ChevronRight,
  RefreshCcw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SidebarProps {
  onNavigateToSchemas?: () => void;
  disabled?: boolean;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function Sidebar({
  onNavigateToSchemas,
  disabled = false,
  collapsed = false,
  onToggleCollapse,
}: SidebarProps = {}) {
  const {
    temas,
    selectedTema,
    setTemas,
    setSelectedTema,
    loading,
    setLoading,
  } = useFileStore();

  const [deletingTema, setDeletingTema] = useState<string | null>(null);

  const renderWithTooltip = (label: string, element: ReactElement) => {
    if (!collapsed) {
      return element;
    }

    return (
      <Tooltip>
        <TooltipTrigger asChild>{element}</TooltipTrigger>
        <TooltipContent side="right" sideOffset={8}>
          {label}
        </TooltipContent>
      </Tooltip>
    );
  };

  useEffect(() => {
    loadTemas();
  }, []);

  const loadTemas = async () => {
    try {
      setLoading(true);
      const response = await api.getTemas();
      setTemas(response.temas);
    } catch (error) {
      console.error("Error loading temas:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTemaSelect = (tema: string | null) => {
    setSelectedTema(tema);
  };

  const handleDeleteTema = async (
    tema: string,
    e: React.MouseEvent<HTMLButtonElement>,
  ) => {
    e.stopPropagation(); // Evitar que se seleccione el tema al hacer clic en el icono

    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el tema "${tema}"?\n\n` +
        `Esto eliminará:\n` +
        `• Todos los archivos del tema en Azure Blob Storage\n` +
        `• La colección "${tema}" en Qdrant (si existe)\n\n` +
        `Esta acción no se puede deshacer.`,
    );

    if (!confirmed) return;

    try {
      setDeletingTema(tema);

      // 1. Eliminar todos los archivos del tema en Azure Blob Storage
      await api.deleteTema(tema);

      // 2. Intentar eliminar la colección en Qdrant (si existe)
      try {
        const collectionExists = await api.checkCollectionExists(tema);
        if (collectionExists.exists) {
          await api.deleteCollection(tema);
          console.log(`Colección "${tema}" eliminada de Qdrant`);
        }
      } catch (error) {
        console.warn(
          `No se pudo eliminar la colección "${tema}" de Qdrant:`,
          error,
        );
        // Continuar aunque falle la eliminación de la colección
      }

      // 3. Actualizar la lista de temas
      await loadTemas();

      // 4. Si el tema eliminado estaba seleccionado, deseleccionar
      if (selectedTema === tema) {
        setSelectedTema(null);
      }
    } catch (error) {
      console.error(`Error eliminando tema "${tema}":`, error);
      alert(
        `Error al eliminar el tema: ${error instanceof Error ? error.message : "Error desconocido"}`,
      );
    } finally {
      setDeletingTema(null);
    }
  };

  return (
    <TooltipProvider delayDuration={100}>
      <div className="bg-white border-r border-gray-200 flex flex-col h-full transition-[width] duration-300">
        {/* Header */}
        <div
          className={cn(
            "border-b border-gray-200 flex items-center gap-3",
            collapsed ? "p-4" : "p-6",
          )}
        >
          <div
            className={cn(
              "flex items-center gap-2 text-gray-900 flex-1",
              collapsed ? "justify-center" : "justify-start",
            )}
          >
            <FileText className="h-6 w-6" />
            {!collapsed && <h1 className="text-xl font-semibold">DoRa Luma</h1>}
          </div>
          {onToggleCollapse && (
            <Button
              variant="ghost"
              size="icon"
              className="text-gray-500 hover:text-gray-900"
              onClick={onToggleCollapse}
              disabled={disabled}
              aria-label={
                collapsed ? "Expandir barra lateral" : "Contraer barra lateral"
              }
            >
              {collapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* Temas List */}
        <div className={cn("flex-1 overflow-y-auto p-4", collapsed && "px-2")}>
          <div className="space-y-1">
            <h2
              className={cn(
                "text-sm font-medium text-gray-500 mb-3",
                collapsed && "text-xs text-center",
              )}
            >
              {collapsed ? "Coll." : "Collections"}
            </h2>

            {/* Todos los archivos */}
            {renderWithTooltip(
              "Todos los archivos",
              <Button
                variant={selectedTema === null ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  collapsed && "px-0 justify-center",
                )}
                onClick={() => handleTemaSelect(null)}
                disabled={disabled}
              >
                <FolderIcon className={cn("h-4 w-4", !collapsed && "mr-2")} />
                <span className={cn("truncate", collapsed && "sr-only")}>
                  Todos los archivos
                </span>
              </Button>,
            )}

            {/* Lista de temas */}
            {loading ? (
              <div className="text-sm text-gray-500 px-3 py-2 text-center">
                {collapsed ? "..." : "Cargando..."}
              </div>
            ) : (
              temas.map((tema) => (
                <div key={tema} className="relative group">
                  {renderWithTooltip(
                    tema,
                    <Button
                      variant={selectedTema === tema ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start",
                        collapsed ? "px-0 justify-center" : "pr-10",
                      )}
                      onClick={() => handleTemaSelect(tema)}
                      disabled={deletingTema === tema || disabled}
                    >
                      <FolderIcon
                        className={cn("h-4 w-4", !collapsed && "mr-2")}
                      />
                      <span className={cn("truncate", collapsed && "sr-only")}>
                        {tema}
                      </span>
                    </Button>,
                  )}
                  {!collapsed && (
                    <button
                      onClick={(e) => handleDeleteTema(tema, e)}
                      disabled={deletingTema === tema || disabled}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded hover:bg-red-100 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                      title="Eliminar tema y colección"
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div
          className={cn(
            "p-4 border-t border-gray-200 space-y-2",
            collapsed && "flex flex-col items-center gap-2",
          )}
        >
          {onNavigateToSchemas &&
            renderWithTooltip(
              "Gestionar Schemas",
              <Button
                variant="default"
                size="sm"
                onClick={onNavigateToSchemas}
                disabled={disabled}
                className={cn(
                  "w-full justify-start",
                  collapsed && "px-0 justify-center",
                )}
              >
                <Database className={cn("h-4 w-4", !collapsed && "mr-2")} />
                <span className={cn(collapsed && "sr-only")}>
                  Gestionar Schemas
                </span>
              </Button>,
            )}
          {renderWithTooltip(
            "Actualizar temas",
            <Button
              variant="outline"
              size="sm"
              onClick={loadTemas}
              disabled={loading || disabled}
              className={cn(
                "w-full justify-start",
                collapsed && "px-0 justify-center",
              )}
            >
              <RefreshCcw className={cn("mr-2 h-4 w-4", collapsed && "mr-0")} />
              <span className={cn(collapsed && "sr-only")}>
                Actualizar temas
              </span>
            </Button>,
          )}
        </div>
      </div>
    </TooltipProvider>
  );
}
