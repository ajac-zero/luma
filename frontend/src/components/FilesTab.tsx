import { useState, useEffect } from "react";
import { useFileStore } from "@/stores/fileStore";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { FileUpload } from "./FileUpload";
import { DeleteConfirmDialog } from "./DeleteConfirmDialog";
import { PDFPreviewModal } from "./PDFPreviewModal";
import { ChunkViewerModal } from "./ChunkViewerModal";
import {
  ChunkingConfigModalLandingAI,
  type LandingAIConfig,
} from "./ChunkingConfigModalLandingAI";
import {
  Upload,
  Download,
  Trash2,
  Search,
  FileText,
  Eye,
  MessageSquare,
  Scissors,
} from "lucide-react";

interface FilesTabProps {
  selectedTema: string | null;
  processing: boolean;
  onProcessingChange?: (isProcessing: boolean) => void;
}

export function FilesTab({
  selectedTema,
  processing,
  onProcessingChange,
}: FilesTabProps) {
  const {
    files,
    setFiles,
    loading,
    setLoading,
    selectedFiles,
    toggleFileSelection,
    selectAllFiles,
    clearSelection,
  } = useFileStore();

  const [searchTerm, setSearchTerm] = useState("");
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [downloading, setDownloading] = useState(false);

  // Estados para el modal de preview de PDF
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewFileUrl, setPreviewFileUrl] = useState<string | null>(null);
  const [previewFileName, setPreviewFileName] = useState("");
  const [previewFileTema, setPreviewFileTema] = useState<string | undefined>(
    undefined,
  );
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Estados para el modal de chunks
  const [chunkViewerOpen, setChunkViewerOpen] = useState(false);
  const [chunkFileName, setChunkFileName] = useState("");
  const [chunkFileTema, setChunkFileTema] = useState("");

  // Estados para chunking
  const [chunkingConfigOpen, setChunkingConfigOpen] = useState(false);
  const [chunkingFileName, setChunkingFileName] = useState("");
  const [chunkingFileTema, setChunkingFileTema] = useState("");
  const [chunkingCollectionName, setChunkingCollectionName] = useState("");

  // Load files when component mounts or selectedTema changes
  useEffect(() => {
    loadFiles();
  }, [selectedTema]);

  const loadFiles = async () => {
    // Don't load files if no dataroom is selected
    if (!selectedTema) {
      setFiles([]);
      return;
    }

    try {
      setLoading(true);
      const response = await api.getFiles(selectedTema);
      setFiles(response.files);
    } catch (error) {
      console.error("Error loading files:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    loadFiles();
  };

  const handleDeleteFile = (filename: string) => {
    setFileToDelete(filename);
    setDeleteDialogOpen(true);
  };

  const handleDeleteSelected = () => {
    if (selectedFiles.size === 0) return;
    setFileToDelete(null);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    try {
      setDeleting(true);

      if (fileToDelete) {
        // Eliminar archivo individual
        await api.deleteFile(fileToDelete, selectedTema || undefined);
      } else {
        // Eliminar archivos seleccionados
        const filesToDelete = Array.from(selectedFiles);
        await api.deleteFiles(filesToDelete, selectedTema || undefined);
        clearSelection();
      }

      await loadFiles();
      setDeleteDialogOpen(false);
      setFileToDelete(null);
    } catch (error) {
      console.error("Error deleting files:", error);
    } finally {
      setDeleting(false);
    }
  };

  const handleDownloadFile = async (filename: string) => {
    try {
      setDownloading(true);
      await api.downloadFile(filename, selectedTema || undefined);
    } catch (error) {
      console.error("Error downloading file:", error);
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadSelected = async () => {
    if (selectedFiles.size === 0) return;

    try {
      setDownloading(true);
      const filesToDownload = Array.from(selectedFiles);
      const zipName = selectedTema
        ? `${selectedTema}_archivos`
        : "archivos_seleccionados";
      await api.downloadMultipleFiles(
        filesToDownload,
        selectedTema || undefined,
        zipName,
      );
      clearSelection();
    } catch (error) {
      console.error("Error downloading files:", error);
    } finally {
      setDownloading(false);
    }
  };

  const handlePreviewFile = async (filename: string) => {
    try {
      setLoadingPreview(true);
      const url = await api.getPreviewUrl(filename, selectedTema || undefined);
      setPreviewFileUrl(url);
      setPreviewFileName(filename);
      setPreviewFileTema(selectedTema || undefined);
      setPreviewModalOpen(true);
    } catch (error) {
      console.error("Error getting preview URL:", error);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleDownloadFromPreview = () => {
    if (previewFileName) {
      handleDownloadFile(previewFileName);
    }
  };

  const handleViewChunks = (filename: string) => {
    setChunkFileName(filename);
    setChunkFileTema(selectedTema || "");
    setChunkViewerOpen(true);
  };

  const handleStartChunking = (filename: string) => {
    setChunkingFileName(filename);
    setChunkingFileTema(selectedTema || "");
    setChunkingCollectionName(selectedTema || "");
    setChunkingConfigOpen(true);
  };

  const handleChunkingProcess = async (config: LandingAIConfig) => {
    try {
      onProcessingChange?.(true);

      const processConfig = {
        file_name: chunkingFileName,
        tema: chunkingFileTema,
        collection_name: chunkingCollectionName,
        mode: config.mode,
        schema_id: config.schemaId,
        include_chunk_types: config.includeChunkTypes,
        max_tokens_per_chunk: config.maxTokensPerChunk,
        merge_small_chunks: config.mergeSmallChunks,
      };

      await api.processWithLandingAI(processConfig);
      console.log("Procesamiento con LandingAI completado");
    } catch (error) {
      console.error("Error en procesamiento con LandingAI:", error);
      throw error;
    } finally {
      onProcessingChange?.(false);
    }
  };

  // Filtrar archivos por término de búsqueda
  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const totalFiles = filteredFiles.length;

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getDeleteDialogProps = () => {
    if (fileToDelete) {
      return {
        title: "Eliminar archivo",
        message: `¿Estás seguro de que deseas eliminar el archivo "${fileToDelete}"?`,
        fileList: [fileToDelete],
      };
    } else {
      const filesToDelete = Array.from(selectedFiles);
      return {
        title: "Eliminar archivos seleccionados",
        message: `¿Estás seguro de que deseas eliminar ${filesToDelete.length} archivo${filesToDelete.length > 1 ? "s" : ""}?`,
        fileList: filesToDelete,
      };
    }
  };

  if (!selectedTema) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <FileText className="w-12 h-12 text-gray-400 mb-4" />
        <p className="text-gray-500">
          Selecciona un dataroom para ver sus archivos
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {processing && (
        <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span className="text-sm text-blue-800">
              Procesando archivos con LandingAI...
            </span>
          </div>
        </div>
      )}

      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Buscar archivos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
              disabled={loading}
            />
          </div>

          <div className="flex items-center gap-2">
            {selectedFiles.size > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadSelected}
                  disabled={downloading}
                  className="gap-2"
                >
                  <Download className="w-4 h-4" />
                  Descargar ({selectedFiles.size})
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeleteSelected}
                  disabled={deleting}
                  className="gap-2 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                  Eliminar ({selectedFiles.size})
                </Button>
              </>
            )}

            <Button
              onClick={() => setUploadDialogOpen(true)}
              disabled={loading}
              className="gap-2"
            >
              <Upload className="w-4 h-4" />
              Subir archivo
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <p className="text-gray-500">Cargando archivos...</p>
            </div>
          ) : filteredFiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64">
              <FileText className="w-12 h-12 text-gray-400 mb-4" />
              <p className="text-gray-500">
                {!selectedTema
                  ? "Selecciona un dataroom para ver sus archivos"
                  : searchTerm
                    ? "No se encontraron archivos"
                    : "No hay archivos en este dataroom"}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={
                        selectedFiles.size === filteredFiles.length &&
                        filteredFiles.length > 0
                      }
                      onCheckedChange={(checked) => {
                        if (checked) {
                          selectAllFiles();
                        } else {
                          clearSelection();
                        }
                      }}
                    />
                  </TableHead>
                  <TableHead>Archivo</TableHead>
                  <TableHead>Tamaño</TableHead>
                  <TableHead>Modificado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredFiles.map((file) => (
                  <TableRow key={file.name}>
                    <TableCell>
                      <Checkbox
                        checked={selectedFiles.has(file.name)}
                        onCheckedChange={() => toggleFileSelection(file.name)}
                      />
                    </TableCell>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        {file.name}
                      </div>
                    </TableCell>
                    <TableCell>{formatFileSize(file.size)}</TableCell>
                    <TableCell>{formatDate(file.last_modified)}</TableCell>
                    <TableCell>
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handlePreviewFile(file.name)}
                          disabled={loadingPreview}
                          className="h-8 w-8 p-0"
                          title="Vista previa"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewChunks(file.name)}
                          className="h-8 w-8 p-0"
                          title="Ver chunks"
                        >
                          <MessageSquare className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStartChunking(file.name)}
                          className="h-8 w-8 p-0"
                          title="Procesar con LandingAI"
                        >
                          <Scissors className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadFile(file.name)}
                          disabled={downloading}
                          className="h-8 w-8 p-0"
                          title="Descargar"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteFile(file.name)}
                          disabled={deleting}
                          className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                          title="Eliminar"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>

      {/* File Upload Modal */}
      <FileUpload
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        onSuccess={handleUploadSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={confirmDelete}
        loading={deleting}
        {...getDeleteDialogProps()}
      />

      {/* PDF Preview Modal */}
      <PDFPreviewModal
        open={previewModalOpen}
        onOpenChange={setPreviewModalOpen}
        fileUrl={previewFileUrl}
        fileName={previewFileName}
        onDownload={handleDownloadFromPreview}
      />

      {/* Chunk Viewer Modal */}
      <ChunkViewerModal
        isOpen={chunkViewerOpen}
        onClose={() => setChunkViewerOpen(false)}
        fileName={chunkFileName}
        tema={chunkFileTema}
      />

      {/* Modal de configuración de chunking con LandingAI */}
      <ChunkingConfigModalLandingAI
        isOpen={chunkingConfigOpen}
        onClose={() => setChunkingConfigOpen(false)}
        onProcess={handleChunkingProcess}
        fileName={chunkingFileName}
        tema={chunkingFileTema}
        collectionName={chunkingCollectionName}
      />
    </div>
  );
}
