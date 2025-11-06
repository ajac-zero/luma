import { useEffect, useState } from "react";
import { useFileStore } from "@/stores/fileStore";
import { api } from "@/services/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FilesTab } from "./FilesTab";
import { DashboardTab } from "./DashboardTab";
import { ChatTab } from "./ChatTab";
import {
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

interface DataroomViewProps {
  onProcessingChange?: (isProcessing: boolean) => void;
}

export function DataroomView({ onProcessingChange }: DataroomViewProps = {}) {
  const { selectedTema, files } = useFileStore();

  // Collection status states
  const [isCheckingCollection, setIsCheckingCollection] = useState(false);
  const [collectionExists, setCollectionExists] = useState<boolean | null>(
    null,
  );
  const [collectionError, setCollectionError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  // Check collection status when tema changes
  useEffect(() => {
    checkCollectionStatus();
  }, [selectedTema]);

  // Load files when tema changes
  useEffect(() => {
    loadFiles();
  }, [selectedTema]);

  const checkCollectionStatus = async () => {
    if (!selectedTema) {
      setCollectionExists(null);
      return;
    }

    setIsCheckingCollection(true);
    setCollectionError(null);

    try {
      const result = await api.checkCollectionExists(selectedTema);
      setCollectionExists(result.exists);
    } catch (err) {
      console.error("Error checking collection:", err);
      setCollectionError(
        err instanceof Error ? err.message : "Error al verificar colección",
      );
      setCollectionExists(null);
    } finally {
      setIsCheckingCollection(false);
    }
  };

  const handleCreateCollection = async () => {
    if (!selectedTema) return;

    setIsCheckingCollection(true);
    setCollectionError(null);

    try {
      const result = await api.createCollection(selectedTema);
      if (result.success) {
        setCollectionExists(true);
        console.log(`Collection "${selectedTema}" created successfully`);
      }
    } catch (err) {
      console.error("Error creating collection:", err);
      setCollectionError(
        err instanceof Error ? err.message : "Error al crear colección",
      );
    } finally {
      setIsCheckingCollection(false);
    }
  };

  const loadFiles = async () => {
    // This will be handled by FilesTab component
  };

  const handleProcessingChange = (isProcessing: boolean) => {
    setProcessing(isProcessing);
    onProcessingChange?.(isProcessing);
  };

  const totalFiles = files.length;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-semibold text-gray-900">
                {selectedTema
                  ? `Dataroom: ${selectedTema}`
                  : "Selecciona un dataroom"}
              </h2>
              {/* Collection Status Indicator */}
              {selectedTema && (
                <div className="flex items-center gap-2">
                  {isCheckingCollection ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                      <span className="text-xs text-gray-500">
                        Verificando...
                      </span>
                    </>
                  ) : collectionExists === true ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-xs text-green-600">
                        Colección disponible
                      </span>
                    </>
                  ) : collectionExists === false ? (
                    <>
                      <AlertCircle className="w-4 h-4 text-yellow-600" />
                      <button
                        onClick={handleCreateCollection}
                        className="text-xs text-yellow-600 hover:text-yellow-700 underline"
                      >
                        Crear colección
                      </button>
                    </>
                  ) : collectionError ? (
                    <>
                      <AlertCircle className="w-4 h-4 text-red-600" />
                      <span className="text-xs text-red-600">
                        Error de conexión
                      </span>
                    </>
                  ) : null}
                </div>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {selectedTema
                ? `${totalFiles} archivo${totalFiles !== 1 ? "s" : ""}`
                : "Selecciona un dataroom de la barra lateral para ver sus archivos"}
            </p>
          </div>
        </div>
      </div>

      <Tabs defaultValue="files" className="flex flex-col flex-1">
        <div className="border-b border-gray-200 px-6 py-2">
          <TabsList className="flex h-10 w-full items-center gap-2 bg-transparent p-0 justify-start">
            <TabsTrigger
              value="overview"
              className="rounded-md px-4 py-2 text-sm font-medium text-gray-600 transition data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:shadow"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="files"
              className="rounded-md px-4 py-2 text-sm font-medium text-gray-600 transition data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:shadow"
            >
              Files
            </TabsTrigger>
            <TabsTrigger
              value="chat"
              className="rounded-md px-4 py-2 text-sm font-medium text-gray-600 transition data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:shadow"
            >
              Chat
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="overview" className="mt-0 flex-1">
          <DashboardTab selectedTema={selectedTema} />
        </TabsContent>

        <TabsContent value="files" className="mt-0 flex flex-1 flex-col">
          <FilesTab
            selectedTema={selectedTema}
            processing={processing}
            onProcessingChange={handleProcessingChange}
          />
        </TabsContent>

        <TabsContent value="chat" className="mt-0 flex-1">
          <ChatTab selectedTema={selectedTema} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
