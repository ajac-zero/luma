import { useState } from "react";
import { useFileStore } from "@/stores/fileStore";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Expand, Minimize2 } from "lucide-react";
import { FilesTab } from "./FilesTab";
import { DashboardTab } from "./DashboardTab";
import { ChatTab } from "./ChatTab";

interface DataroomViewProps {
  onProcessingChange?: (isProcessing: boolean) => void;
}

export function DataroomView({ onProcessingChange }: DataroomViewProps = {}) {
  const { selectedTema } = useFileStore();

  const [processing, setProcessing] = useState(false);
  const [fullscreenTab, setFullscreenTab] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState("overview");

  const handleProcessingChange = (isProcessing: boolean) => {
    setProcessing(isProcessing);
    onProcessingChange?.(isProcessing);
  };

  const openFullscreen = (tabValue: string) => {
    setFullscreenTab(tabValue);
  };

  const closeFullscreen = () => {
    setFullscreenTab(null);
  };

  const renderTabContent = (tabValue: string, isFullscreen = false) => {
    const className = isFullscreen ? "h-[calc(100vh-8rem)] flex flex-col" : "";

    switch (tabValue) {
      case "overview":
        return (
          <div className={className}>
            <DashboardTab selectedTema={selectedTema} />
          </div>
        );
      case "files":
        return (
          <div className={className}>
            <FilesTab
              selectedTema={selectedTema}
              processing={processing}
              onProcessingChange={handleProcessingChange}
            />
          </div>
        );
      case "chat":
        return (
          <div className={className}>
            <ChatTab selectedTema={selectedTema} />
          </div>
        );
      default:
        return null;
    }
  };

  const getTabTitle = (tabValue: string) => {
    switch (tabValue) {
      case "overview":
        return "Overview";
      case "files":
        return "Files";
      case "chat":
        return "Chat";
      default:
        return "";
    }
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

      <Tabs
        value={currentTab}
        onValueChange={setCurrentTab}
        className="flex flex-col flex-1"
      >
        <div className="border-b border-gray-200 px-6 py-2">
          <TabsList className="flex h-10 w-full items-center gap-2 bg-transparent p-0 justify-between">
            <div className="flex items-center gap-2">
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
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => openFullscreen(currentTab)}
              className="ml-auto"
            >
              <Expand className="h-4 w-4" />
              <span className="sr-only">Open fullscreen</span>
            </Button>
          </TabsList>
        </div>

        <TabsContent value="overview" className="mt-0 flex-1">
          {renderTabContent("overview")}
        </TabsContent>

        <TabsContent value="files" className="mt-0 flex flex-1 flex-col">
          {renderTabContent("files")}
        </TabsContent>

        <TabsContent value="chat" className="mt-0 flex-1">
          {renderTabContent("chat")}
        </TabsContent>
      </Tabs>

      <Dialog
        open={fullscreenTab !== null}
        onOpenChange={(open: boolean) => !open && closeFullscreen()}
      >
        <DialogContent className="max-w-[100vw] max-h-[100vh] w-[100vw] h-[100vh] m-0 rounded-none [&>button]:hidden">
          <DialogHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <DialogTitle className="text-xl font-semibold">
              {selectedTema
                ? `${getTabTitle(fullscreenTab || "")} - ${selectedTema}`
                : getTabTitle(fullscreenTab || "")}
            </DialogTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={closeFullscreen}
              className="h-8 w-8 p-0"
            >
              <Minimize2 className="h-4 w-4" />
              <span className="sr-only">Exit fullscreen</span>
            </Button>
          </DialogHeader>

          <div className="flex-1 overflow-hidden">
            {fullscreenTab && renderTabContent(fullscreenTab, true)}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
