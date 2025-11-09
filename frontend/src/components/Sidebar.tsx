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
  Plus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

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
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newDataroomName, setNewDataroomName] = useState("");
  const [creatingDataroom, setCreatingDataroom] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

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

  const handleCreateDialogOpenChange = (open: boolean) => {
    setCreateDialogOpen(open);
    if (!open) {
      setNewDataroomName("");
      setCreateError(null);
    }
  };

  const handleCreateDataroom = async () => {
    const trimmed = newDataroomName.trim();
    if (!trimmed) {
      setCreateError("Name is required");
      return;
    }

    setCreatingDataroom(true);
    setCreateError(null);

    try {
      const result = await api.createDataroom({ name: trimmed });

      // Refresh the datarooms list (this will load all datarooms including the new one)

      await loadTemas();

      // Select the newly created dataroom
      setSelectedTema(trimmed);

      // Close dialog and show success
      handleCreateDialogOpenChange(false);
    } catch (error) {
      console.error("Error creating dataroom:", error);
      setCreateError(
        error instanceof Error
          ? error.message
          : "Could not create the dataroom. Please try again.",
      );
    } finally {
      setCreatingDataroom(false);
    }
  };

  useEffect(() => {
    loadTemas();
  }, []);

  const loadTemas = async () => {
    try {
      setLoading(true);
      const response = await api.getDatarooms();

      // Extract dataroom names from the response with better error handling
      let dataroomNames: string[] = [];
      if (response && response.datarooms && Array.isArray(response.datarooms)) {
        dataroomNames = response.datarooms
          .filter((dataroom) => dataroom && dataroom.name)
          .map((dataroom) => dataroom.name);
      }

      setTemas(dataroomNames);
      // Auto-select first dataroom if none is selected and datarooms are available
      if (!selectedTema && dataroomNames.length > 0) {
        setSelectedTema(dataroomNames[0]);
      }
    } catch (error) {
      console.error("Error loading datarooms:", error);
      // Fallback to legacy getTemas if dataroom endpoint fails
      try {
        const legacyResponse = await api.getTemas();
        const legacyTemas = Array.isArray(legacyResponse?.temas)
          ? legacyResponse.temas.filter(Boolean)
          : [];
        setTemas(legacyTemas);
        // Auto-select first legacy tema if none is selected
        if (!selectedTema && legacyTemas.length > 0) {
          setSelectedTema(legacyTemas[0]);
        }
      } catch (legacyError) {
        console.error("Error loading legacy temas:", legacyError);
        // Ensure we always set an array, never undefined or null
        setTemas([]);
      }
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
    e.stopPropagation(); // Prevent selecting the dataroom when clicking delete

    const confirmed = window.confirm(
      `Are you sure you want to delete the dataroom "${tema}"?\n\n` +
        `This will remove:\n` +
        `• The dataroom from the database\n` +
        `• All files stored for this topic in Azure Blob Storage\n` +
        `• The "${tema}" collection in Qdrant (if it exists)\n\n` +
        `This action cannot be undone.`,
    );

    if (!confirmed) return;

    try {
      setDeletingTema(tema);

      // 1. Delete the dataroom (this will also delete the vector collection)
      try {
        await api.deleteDataroom(tema);
      } catch (error) {
        console.error(`Error deleting dataroom "${tema}":`, error);
        // If dataroom deletion fails, fall back to legacy deletion

        // Delete all topic files in Azure Blob Storage
        await api.deleteTema(tema);

        // Attempt to delete the Qdrant collection (if it exists)
        try {
          const collectionExists = await api.checkCollectionExists(tema);
          if (collectionExists.exists) {
            await api.deleteCollection(tema);
          }
        } catch (collectionError) {
          console.warn(
            `Could not delete the "${tema}" collection from Qdrant:`,
            collectionError,
          );
        }
      }

      // 2. Actualizar la lista de temas
      await loadTemas();

      // 3. Si el tema eliminado estaba seleccionado, deseleccionar
      if (selectedTema === tema) {
        setSelectedTema(null);
      }
    } catch (error) {
      console.error(`Error deleting dataroom "${tema}":`, error);
      alert(
        `Unable to delete dataroom: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    } finally {
      setDeletingTema(null);
    }
  };

  return (
    <TooltipProvider delayDuration={100}>
      <div className="bg-slate-800 border-r border-slate-700 flex flex-col h-full transition-[width] duration-300">
        {/* Header */}
        <div
          className={cn(
            "border-b border-slate-700 flex items-center gap-3",
            collapsed ? "p-4" : "p-6",
          )}
        >
          <div
            className={cn(
              "flex items-center gap-2 text-slate-100 flex-1",
              collapsed ? "justify-center" : "justify-start",
            )}
          >
            <FileText className="h-6 w-6" />
            {!collapsed && <h1 className="text-xl font-semibold">Luma</h1>}
          </div>
          {onToggleCollapse && (
            <Button
              variant="ghost"
              size="icon"
              className="text-slate-400 hover:text-slate-100"
              onClick={onToggleCollapse}
              disabled={disabled}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
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
            <div
              className={cn(
                "mb-3 flex items-center",
                collapsed ? "justify-center" : "justify-between",
              )}
            >
              {!collapsed && (
                <h2 className="text-sm font-medium text-slate-300">
                  Datarooms
                </h2>
              )}
              {renderWithTooltip(
                "Create",
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "gap-2 bg-slate-700/50 text-slate-200 hover:bg-slate-600 hover:text-slate-100 border border-slate-600",
                    collapsed
                      ? "h-10 w-10 p-0 justify-center rounded-full"
                      : "",
                  )}
                  onClick={() => handleCreateDialogOpenChange(true)}
                  disabled={disabled || creatingDataroom}
                >
                  <Plus className="h-4 w-4" />
                  {!collapsed && <span>Create</span>}
                </Button>,
              )}
            </div>

            {/* Dataroom list */}
            {loading ? (
              <div className="text-sm text-slate-400 px-3 py-2 text-center">
                {collapsed ? "..." : "Loading..."}
              </div>
            ) : Array.isArray(temas) && temas.length > 0 ? (
              temas.map((tema) => (
                <div key={tema} className="relative group">
                  {renderWithTooltip(
                    tema,
                    <Button
                      variant={selectedTema === tema ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start text-slate-300 hover:bg-slate-700 hover:text-slate-100",
                        selectedTema === tema && "bg-slate-700 text-slate-100",
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
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded hover:bg-red-500/20 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                      title="Delete dataroom and collection"
                    >
                      <Trash2 className="h-4 w-4 text-red-400" />
                    </button>
                  )}
                </div>
              ))
            ) : (
              <div className="text-sm text-slate-400 px-3 py-2 text-center">
                {Array.isArray(temas) && temas.length === 0
                  ? "No datarooms found"
                  : "Loading datarooms..."}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div
          className={cn(
            "p-4 border-t border-slate-700 space-y-2",
            collapsed && "flex flex-col items-center gap-2",
          )}
        >
          {onNavigateToSchemas &&
            renderWithTooltip(
              "Manage schemas",
              <Button
                variant="default"
                size="sm"
                onClick={onNavigateToSchemas}
                disabled={disabled}
                className={cn(
                  "w-full justify-start bg-slate-700 text-slate-100 hover:bg-slate-600",
                  collapsed && "px-0 justify-center",
                )}
              >
                <Database className={cn("h-4 w-4", !collapsed && "mr-2")} />
                <span className={cn(collapsed && "sr-only")}>
                  Manage Schemas
                </span>
              </Button>,
            )}
          {renderWithTooltip(
            "Refresh datarooms",
            <Button
              variant="ghost"
              size="sm"
              onClick={loadTemas}
              disabled={loading || disabled}
              className={cn(
                "w-full justify-start bg-slate-700/50 text-slate-200 hover:bg-slate-600 hover:text-slate-100 border border-slate-600",
                collapsed && "px-0 justify-center",
              )}
            >
              <RefreshCcw className={cn("mr-2 h-4 w-4", collapsed && "mr-0")} />
              <span className={cn(collapsed && "sr-only")}>
                Refresh datarooms
              </span>
            </Button>,
          )}
        </div>
      </div>
      <Dialog
        open={createDialogOpen}
        onOpenChange={handleCreateDialogOpenChange}
      >
        <DialogContent
          className="max-w-sm"
          aria-describedby="create-dataroom-description"
        >
          <DialogHeader>
            <DialogTitle>Create dataroom</DialogTitle>
            <DialogDescription id="create-dataroom-description">
              Choose a unique name to organize your files.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="dataroom-name">Dataroom name</Label>
              <Input
                id="dataroom-name"
                value={newDataroomName}
                onChange={(e) => {
                  setNewDataroomName(e.target.value);
                  if (createError) {
                    setCreateError(null);
                  }
                }}
                placeholder="e.g., policies, contracts, finance..."
                autoFocus
              />
              {createError && (
                <p className="text-sm text-red-500">{createError}</p>
              )}
            </div>
          </div>
          <DialogFooter className="mt-4">
            <Button
              variant="outline"
              onClick={() => handleCreateDialogOpenChange(false)}
              disabled={creatingDataroom}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateDataroom}
              disabled={creatingDataroom || newDataroomName.trim() === ""}
            >
              {creatingDataroom ? "Creating…" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </TooltipProvider>
  );
}
