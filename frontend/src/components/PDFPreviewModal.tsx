import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import {
  Download,
  Loader2,
  FileText,
  ExternalLink
} from 'lucide-react'

interface PDFPreviewModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  fileUrl: string | null
  fileName: string
  onDownload?: () => void
}

export function PDFPreviewModal({
  open,
  onOpenChange,
  fileUrl,
  fileName,
  onDownload
}: PDFPreviewModalProps) {
  // Estado para manejar el loading del iframe
  const [loading, setLoading] = useState(true)

  // Efecto para manejar el timeout del loading
  useEffect(() => {
    if (open && fileUrl) {
      setLoading(true)

      // Timeout para ocultar loading automáticamente después de 3 segundos
      // Algunos iframes no disparan onLoad correctamente
      const timeout = setTimeout(() => {
        setLoading(false)
      }, 3000)

      return () => clearTimeout(timeout)
    }
  }, [open, fileUrl])

  // Manejar cuando el iframe termina de cargar
  const handleIframeLoad = () => {
    setLoading(false)
  }

  // Abrir PDF en nueva pestaña
  const openInNewTab = () => {
    if (fileUrl) {
      window.open(fileUrl, '_blank')
    }
  }

  // Reiniciar loading cuando cambia el archivo
  const handleOpenChange = (open: boolean) => {
    if (open) {
      setLoading(true)
    }
    onOpenChange(open)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-6xl max-h-[95vh] h-[95vh] flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {fileName}
          </DialogTitle>
          <DialogDescription>
            Vista previa del documento PDF
          </DialogDescription>
        </DialogHeader>

        {/* Barra de controles */}
        <div className="flex items-center justify-between gap-4 px-6 py-3 border-b bg-gray-50">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={openInNewTab}
              title="Abrir en nueva pestaña"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Abrir en pestaña nueva
            </Button>
          </div>

          {/* Botón de descarga */}
          {onDownload && (
            <Button
              variant="outline"
              size="sm"
              onClick={onDownload}
              title="Descargar archivo"
            >
              <Download className="w-4 h-4 mr-2" />
              Descargar
            </Button>
          )}
        </div>

        {/* Área de visualización del PDF con iframe */}
        <div className="flex-1 relative bg-gray-100">
          {!fileUrl ? (
            <div className="flex items-center justify-center h-full text-center text-gray-500 p-8">
              <div>
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p>No se ha proporcionado un archivo para previsualizar</p>
              </div>
            </div>
          ) : (
            <>
              {/* Indicador de carga */}
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
                  <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
                    <p className="text-gray-600">Cargando PDF...</p>
                  </div>
                </div>
              )}

              {/*
                Iframe para mostrar el PDF
                El navegador maneja toda la visualización, zoom, scroll, etc.
                Esto muestra el PDF exactamente como se vería si lo abrieras directamente
              */}
              <iframe
                src={fileUrl}
                className="w-full h-full border-0"
                title={`Vista previa de ${fileName}`}
                onLoad={handleIframeLoad}
                style={{ minHeight: '600px' }}
              />
            </>
          )}
        </div>

        {/* Footer con información */}
        <div className="px-6 py-3 border-t bg-gray-50 text-xs text-gray-500 text-center">
          {fileName}
        </div>
      </DialogContent>
    </Dialog>
  )
}
