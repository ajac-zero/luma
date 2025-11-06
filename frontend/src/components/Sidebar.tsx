import { useEffect, useState } from 'react'
import { useFileStore } from '@/stores/fileStore'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { FolderIcon, FileText, Trash2, Database } from 'lucide-react'

interface SidebarProps {
  onNavigateToSchemas?: () => void
  disabled?: boolean
}

export function Sidebar({ onNavigateToSchemas, disabled = false }: SidebarProps = {}) {
  const {
    temas,
    selectedTema,
    setTemas,
    setSelectedTema,
    loading,
    setLoading
  } = useFileStore()

  const [deletingTema, setDeletingTema] = useState<string | null>(null)

  useEffect(() => {
    loadTemas()
  }, [])

  const loadTemas = async () => {
    try {
      setLoading(true)
      const response = await api.getTemas()
      setTemas(response.temas)
    } catch (error) {
      console.error('Error loading temas:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTemaSelect = (tema: string | null) => {
    setSelectedTema(tema)
  }

  const handleDeleteTema = async (tema: string, e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation() // Evitar que se seleccione el tema al hacer clic en el icono

    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar el tema "${tema}"?\n\n` +
      `Esto eliminará:\n` +
      `• Todos los archivos del tema en Azure Blob Storage\n` +
      `• La colección "${tema}" en Qdrant (si existe)\n\n` +
      `Esta acción no se puede deshacer.`
    )

    if (!confirmed) return

    try {
      setDeletingTema(tema)

      // 1. Eliminar todos los archivos del tema en Azure Blob Storage
      await api.deleteTema(tema)

      // 2. Intentar eliminar la colección en Qdrant (si existe)
      try {
        const collectionExists = await api.checkCollectionExists(tema)
        if (collectionExists.exists) {
          await api.deleteCollection(tema)
          console.log(`Colección "${tema}" eliminada de Qdrant`)
        }
      } catch (error) {
        console.warn(`No se pudo eliminar la colección "${tema}" de Qdrant:`, error)
        // Continuar aunque falle la eliminación de la colección
      }

      // 3. Actualizar la lista de temas
      await loadTemas()

      // 4. Si el tema eliminado estaba seleccionado, deseleccionar
      if (selectedTema === tema) {
        setSelectedTema(null)
      }

    } catch (error) {
      console.error(`Error eliminando tema "${tema}":`, error)
      alert(`Error al eliminar el tema: ${error instanceof Error ? error.message : 'Error desconocido'}`)
    } finally {
      setDeletingTema(null)
    }
  }

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="h-6 w-6" />
          DoRa Luma
        </h1>
      </div>

      {/* Temas List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          <h2 className="text-sm font-medium text-gray-500 mb-3">Collections</h2>
          
          {/* Todos los archivos */}
          <Button
            variant={selectedTema === null ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => handleTemaSelect(null)}
            disabled={disabled}
          >
            <FolderIcon className="mr-2 h-4 w-4" />
            Todos los archivos
          </Button>

          {/* Lista de temas */}
          {loading ? (
            <div className="text-sm text-gray-500 px-3 py-2">Cargando...</div>
          ) : (
            temas.map((tema) => (
              <div key={tema} className="relative group">
                <Button
                  variant={selectedTema === tema ? "secondary" : "ghost"}
                  className="w-full justify-start pr-10"
                  onClick={() => handleTemaSelect(tema)}
                  disabled={deletingTema === tema || disabled}
                >
                  <FolderIcon className="mr-2 h-4 w-4" />
                  {tema}
                </Button>
                <button
                  onClick={(e) => handleDeleteTema(tema, e)}
                  disabled={deletingTema === tema || disabled}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded hover:bg-red-100 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                  title="Eliminar tema y colección"
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 space-y-2">
        {onNavigateToSchemas && (
          <Button
            variant="default"
            size="sm"
            onClick={onNavigateToSchemas}
            disabled={disabled}
            className="w-full"
          >
            <Database className="mr-2 h-4 w-4" />
            Gestionar Schemas
          </Button>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={loadTemas}
          disabled={loading || disabled}
          className="w-full"
        >
          Actualizar temas
        </Button>
      </div>
    </div>
  )
}