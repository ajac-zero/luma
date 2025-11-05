import { useEffect, useState } from 'react'
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
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'

interface CollectionVerifierProps {
  tema: string | null
  onVerified?: (exists: boolean) => void
}

export function CollectionVerifier({ tema, onVerified }: CollectionVerifierProps) {
  const [isChecking, setIsChecking] = useState(false)
  const [collectionExists, setCollectionExists] = useState<boolean | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (tema) {
      checkCollection()
    } else {
      setCollectionExists(null)
    }
  }, [tema])

  const checkCollection = async () => {
    if (!tema) return

    setIsChecking(true)
    setError(null)

    try {
      const result = await api.checkCollectionExists(tema)
      setCollectionExists(result.exists)

      // Si no existe, mostrar el diálogo de confirmación
      if (!result.exists) {
        setShowCreateDialog(true)
      }

      onVerified?.(result.exists)
    } catch (err) {
      console.error('Error checking collection:', err)
      setError(err instanceof Error ? err.message : 'Error al verificar colección')
      setCollectionExists(null)
    } finally {
      setIsChecking(false)
    }
  }

  const handleCreateCollection = async () => {
    if (!tema) return

    setIsCreating(true)
    setError(null)

    try {
      const result = await api.createCollection(tema)

      if (result.success) {
        setCollectionExists(true)
        setShowCreateDialog(false)
        onVerified?.(true)
      }
    } catch (err) {
      console.error('Error creating collection:', err)
      setError(err instanceof Error ? err.message : 'Error al crear colección')
    } finally {
      setIsCreating(false)
    }
  }

  const handleCancelCreate = () => {
    setShowCreateDialog(false)
    // Opcionalmente podemos notificar que no se creó la colección
    onVerified?.(false)
  }

  // No renderizar nada si no hay tema seleccionado
  if (!tema) {
    return null
  }

  return (
    <>
      {/* Indicador de estado de la colección */}
      {isChecking ? (
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Verificando colección...</span>
        </div>
      ) : collectionExists === true ? (
        <div className="flex items-center gap-2 text-sm text-green-600 mb-4">
          <CheckCircle2 className="w-4 h-4" />
          <span>Colección "{tema}" disponible en Qdrant</span>
        </div>
      ) : collectionExists === false ? (
        <div className="flex items-center gap-2 text-sm text-yellow-600 mb-4">
          <AlertCircle className="w-4 h-4" />
          <span>Colección "{tema}" no existe en Qdrant</span>
        </div>
      ) : error ? (
        <div className="flex items-center gap-2 text-sm text-red-600 mb-4">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : null}

      {/* Diálogo de confirmación para crear colección */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Crear colección en Qdrant</DialogTitle>
            <DialogDescription>
              La colección "<strong>{tema}</strong>" no existe en la base de datos vectorial.
              <br />
              <br />
              ¿Deseas crear esta colección ahora? Esto permitirá almacenar y buscar chunks de
              documentos para este tema.
            </DialogDescription>
          </DialogHeader>

          {error && (
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelCreate}
              disabled={isCreating}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleCreateCollection}
              disabled={isCreating}
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creando...
                </>
              ) : (
                'Crear colección'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
