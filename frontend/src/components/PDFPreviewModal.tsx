import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Download, Loader2, FileText, ExternalLink } from "lucide-react";

interface PDFPreviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fileUrl: string | null;
  fileName: string;
  onDownload?: () => void;
}

export function PDFPreviewModal({
  open,
  onOpenChange,
  fileUrl,
  fileName,
  onDownload,
}: PDFPreviewModalProps) {
  // Track iframe loading state
  const [loading, setLoading] = useState(true);

  // Hide loading if iframe never fires onLoad
  useEffect(() => {
    if (open && fileUrl) {
      setLoading(true);

      const timeout = setTimeout(() => {
        setLoading(false);
      }, 3000);

      return () => clearTimeout(timeout);
    }
  }, [open, fileUrl]);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const openInNewTab = () => {
    if (fileUrl) {
      window.open(fileUrl, "_blank");
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (open) {
      setLoading(true);
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-6xl max-h-[95vh] h-[95vh] flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {fileName}
          </DialogTitle>
          <DialogDescription>PDF preview</DialogDescription>
        </DialogHeader>

        {/* Controls */}
        <div className="flex items-center justify-between gap-4 px-6 py-3 border-b bg-gray-50">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={openInNewTab}
              title="Open in new tab"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Open in new tab
            </Button>
          </div>

          {/* Download button */}
          {onDownload && (
            <Button
              variant="outline"
              size="sm"
              onClick={onDownload}
              title="Download file"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          )}
        </div>

        {/* PDF iframe */}
        <div className="flex-1 relative bg-gray-100 overflow-hidden min-h-0">
          {!fileUrl ? (
            <div className="flex items-center justify-center h-full text-center text-gray-500 p-8">
              <div>
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p>No file available for preview</p>
              </div>
            </div>
          ) : (
            <>
              {/* Loading state */}
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
                  <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
                    <p className="text-gray-600">Loading PDF…</p>
                  </div>
                </div>
              )}

              <iframe
                src={fileUrl}
                className="w-full h-full border-0"
                title={`Preview of ${fileName}`}
                onLoad={handleIframeLoad}
              />
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
