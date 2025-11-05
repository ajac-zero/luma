import { useEffect, useState } from 'react'
import { api } from '../services/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog'
import { Button } from './ui/button'
import { AlertCircle, Loader2, FileText, Trash2 } from 'lucide-react'

interface ChunkViewerModalProps {
  isOpen: boolean
  onClose: () => void
  fileName: string
  tema: string
}

interface Chunk {
  id: string
  payload: {
    page_content: string
    metadata: {
      file_name: string
      page: number
      [key: string]: any
    }
    [key: string]: any
  }
  vector?: number[]
}

export function ChunkViewerModal({ isOpen, onClose, fileName, tema }: ChunkViewerModalProps) {
  const [chunks, setChunks] = useState<Chunk[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (isOpen && fileName && tema) {
      loadChunks()
    }
  }, [isOpen, fileName, tema])

  const loadChunks = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await api.getChunksByFile(tema, fileName)
      setChunks(result.chunks)
    } catch (err) {
      console.error('Error loading chunks:', err)
      setError(err instanceof Error ? err.message : 'Error al cargar chunks')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteFile = async () => {
    if (!confirm(`¿Estás seguro de eliminar todos los chunks del archivo "${fileName}" de la colección "${tema}"?`)) {
      return
    }

    setDeleting(true)
    setError(null)

    try {
      await api.deleteFileFromCollection(tema, fileName)
      alert('Archivo eliminado de la colección exitosamente')
      onClose()
    } catch (err) {
      console.error('Error deleting file from collection:', err)
      setError(err instanceof Error ? err.message : 'Error al eliminar archivo')
    } finally {
      setDeleting(false)
    }
  }

  const handleClose = () => {
    setChunks([])
    setError(null)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Chunks de "{fileName}"
          </DialogTitle>
          <DialogDescription>
            Colección: <strong>{tema}</strong>
          </DialogDescription>
        </DialogHeader>

        {/* Contenido */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              <span className="ml-2 text-gray-500">Cargando chunks...</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-4 rounded">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          ) : chunks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No se encontraron chunks para este archivo.</p>
              <p className="text-sm mt-1">El archivo aún no ha sido procesado o no existe en la colección.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Estadísticas */}
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-sm text-blue-800">
                  <strong>Total de chunks:</strong> {chunks.length}
                </p>
              </div>

              {/* Lista de chunks */}
              {chunks.map((chunk, index) => (
                <div key={chunk.id} className="border rounded-lg p-4 space-y-2">
                  {/* Header del chunk */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-700">
                        Chunk #{index + 1}
                      </span>
                      <span className="text-xs text-gray-500">
                        Página {chunk.payload.metadata.page}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400 font-mono">
                      ID: {chunk.id.substring(0, 8)}...
                    </span>
                  </div>

                  {/* Texto del chunk */}
                  {chunk.payload.page_content && (
                    <div className="bg-gray-50 p-3 rounded text-sm">
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {chunk.payload.page_content}
                      </p>
                      <div className="mt-2 text-xs text-gray-500">
                        <strong>Caracteres:</strong> {chunk.payload.page_content.length}
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="text-xs text-gray-500">
                    <strong>Metadata:</strong>
                    <pre className="mt-1 bg-gray-100 p-2 rounded overflow-x-auto">
                      {JSON.stringify(chunk.payload.metadata, null, 2)}
                    </pre>
                  </div>

                  {/* Información del vector (opcional) */}
                  {chunk.vector && (
                    <div className="text-xs text-gray-400">
                      Vector dimension: {chunk.vector.length}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer con acciones */}
        <div className="flex justify-between items-center pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleDeleteFile}
            disabled={deleting || chunks.length === 0}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            {deleting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Eliminando...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Eliminar de colección
              </>
            )}
          </Button>

          <Button onClick={handleClose}>
            Cerrar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
