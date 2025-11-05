import { useState, useEffect } from 'react'
import { api } from '../services/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog'
import { Button } from './ui/button'
import { AlertCircle, Loader2, FileText, CheckCircle2, XCircle } from 'lucide-react'
import type { ChunkingConfig } from './ChunkingConfigModal'

interface ChunkPreviewPanelProps {
  isOpen: boolean
  onClose: () => void
  config: ChunkingConfig | null
  onAccept: (config: ChunkingConfig) => void
  onCancel: () => void
}

interface PreviewChunk {
  index: number
  text: string
  page: number
  file_name: string
  tokens: number
}

export function ChunkPreviewPanel({
  isOpen,
  onClose,
  config,
  onAccept,
  onCancel,
}: ChunkPreviewPanelProps) {
  const [chunks, setChunks] = useState<PreviewChunk[]>([])
  const [loading, setLoading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Auto-cargar preview cuando se abre el modal
  useEffect(() => {
    if (isOpen && config && chunks.length === 0) {
      loadPreview()
    }
  }, [isOpen, config])

  const loadPreview = async () => {
    if (!config) return

    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const result = await api.generateChunkPreview(config)
      setChunks(result.chunks)
    } catch (err) {
      console.error('Error loading preview:', err)
      setError(err instanceof Error ? err.message : 'Error generando preview')
    } finally {
      setLoading(false)
    }
  }

  const handleAccept = async () => {
    if (!config) return

    setProcessing(true)
    setError(null)

    try {
      await onAccept(config)
      setSuccess(true)

      // Cerrar después de 2 segundos
      setTimeout(() => {
        handleClose()
      }, 2000)
    } catch (err) {
      console.error('Error processing:', err)
      setError(err instanceof Error ? err.message : 'Error procesando PDF')
    } finally {
      setProcessing(false)
    }
  }

  const handleCancel = () => {
    onCancel()
    handleClose()
  }

  const handleClose = () => {
    setChunks([])
    setError(null)
    setSuccess(false)
    onClose()
  }

  if (!config) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Preview de Chunks
          </DialogTitle>
          <DialogDescription>
            Vista previa de chunks para <strong>{config.file_name}</strong>
          </DialogDescription>
        </DialogHeader>

        {/* Contenido */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              <span className="ml-2 text-gray-500">Generando preview...</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-4 rounded">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          ) : success ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <CheckCircle2 className="w-16 h-16 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold text-green-700">
                Procesamiento Completado
              </h3>
              <p className="text-sm text-gray-600 mt-2">
                El PDF ha sido procesado y subido a Qdrant exitosamente
              </p>
            </div>
          ) : chunks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No hay chunks para mostrar</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Información de configuración */}
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-sm text-blue-800">
                  <strong>Configuración:</strong> Max {config.max_tokens} tokens, Target{' '}
                  {config.target_tokens} tokens
                  {config.use_llm && ' | LLM Habilitado'}
                </p>
              </div>

              {/* Lista de chunks */}
              {chunks.map((chunk) => (
                <div key={chunk.index} className="border rounded-lg p-4 space-y-2">
                  {/* Header del chunk */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-700">
                        Chunk #{chunk.index + 1}
                      </span>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        Página {chunk.page}
                      </span>
                      <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                        ~{chunk.tokens} tokens
                      </span>
                    </div>
                  </div>

                  {/* Texto del chunk */}
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {chunk.text}
                    </p>
                  </div>

                  {/* Indicador de longitud */}
                  <div className="text-xs text-gray-500">
                    Longitud: {chunk.text.length} caracteres
                  </div>
                </div>
              ))}

              {/* Información adicional */}
              <div className="bg-yellow-50 border border-yellow-200 p-3 rounded">
                <p className="text-sm text-yellow-800">
                  <strong>Nota:</strong> Estos son chunks de ejemplo (hasta 3). El documento
                  completo generará más chunks según su tamaño.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer con acciones */}
        <DialogFooter className="flex justify-between items-center pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={processing || success}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <XCircle className="w-4 h-4 mr-2" />
            Cancelar
          </Button>

          <Button onClick={handleAccept} disabled={processing || loading || chunks.length === 0 || success}>
            {processing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Procesando...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Aceptar y Procesar
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
