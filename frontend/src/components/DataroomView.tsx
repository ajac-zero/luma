import { useEffect, useState } from "react";
import { useFileStore } from "@/stores/fileStore";
import { api } from "@/services/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FilesTab } from "./FilesTab";
import { DashboardTab } from "./DashboardTab";
import { ChatTab } from "./ChatTab";

interface DataroomViewProps {
  onProcessingChange?: (isProcessing: boolean) => void;
}

export function DataroomView({ onProcessingChange }: DataroomViewProps = {}) {
  const { selectedTema, files } = useFileStore();

  const [processing, setProcessing] = useState(false);

  const handleProcessingChange = (isProcessing: boolean) => {
    setProcessing(isProcessing);
    onProcessingChange?.(isProcessing);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {selectedTema
                ? `Dataroom: ${selectedTema}`
                : "Selecciona un dataroom"}
            </h2>
            <p className="text-sm text-gray-600">
              {selectedTema
                ? "Gestiona archivos, consulta métricas y chatea con IA sobre el contenido"
                : "Selecciona un dataroom de la barra lateral para comenzar"}
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
