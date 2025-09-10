import { useEffect } from 'react'
import { useFileStore } from '@/stores/fileStore'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { FolderIcon, FileText } from 'lucide-react'

export function Sidebar() {
  const { 
    temas, 
    selectedTema, 
    setTemas, 
    setSelectedTema, 
    loading,
    setLoading 
  } = useFileStore()

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

  return (
    <div className="bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <FileText className="h-6 w-6" />
          DoRa Banorte
        </h1>
      </div>

      {/* Temas List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          <h2 className="text-sm font-medium text-gray-500 mb-3">TEMAS</h2>
          
          {/* Todos los archivos */}
          <Button
            variant={selectedTema === null ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => handleTemaSelect(null)}
          >
            <FolderIcon className="mr-2 h-4 w-4" />
            Todos los archivos
          </Button>

          {/* Lista de temas */}
          {loading ? (
            <div className="text-sm text-gray-500 px-3 py-2">Cargando...</div>
          ) : (
            temas.map((tema) => (
              <Button
                key={tema}
                variant={selectedTema === tema ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => handleTemaSelect(tema)}
              >
                <FolderIcon className="mr-2 h-4 w-4" />
                {tema}
              </Button>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <Button
          variant="outline"
          size="sm"
          onClick={loadTemas}
          disabled={loading}
          className="w-full"
        >
          Actualizar temas
        </Button>
      </div>
    </div>
  )
}