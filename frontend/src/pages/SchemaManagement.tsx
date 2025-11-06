/**
 * Schema Management Page
 * Página principal para gestionar schemas personalizados
 */
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Plus, ArrowLeft } from 'lucide-react'
import { SchemaBuilder } from '@/components/schemas/SchemaBuilder'
import { SchemaList } from '@/components/schemas/SchemaList'
import { useFileStore } from '@/stores/fileStore'
import { api } from '@/services/api'
import type { CustomSchema } from '@/types/schema'

type View = 'list' | 'create' | 'edit'

export function SchemaManagement() {
  const { selectedTema } = useFileStore()
  const [view, setView] = useState<View>('list')
  const [schemas, setSchemas] = useState<CustomSchema[]>([])
  const [selectedSchema, setSelectedSchema] = useState<CustomSchema | undefined>()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSchemas()
  }, [selectedTema])

  const loadSchemas = async () => {
    setLoading(true)
    try {
      const data = await api.listSchemas(selectedTema || undefined)
      setSchemas(data)
    } catch (error: any) {
      console.error('Error loading schemas:', error)
      alert('Error cargando schemas: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (schema: CustomSchema) => {
    try {
      if (selectedSchema?.schema_id) {
        // Update existing
        await api.updateSchema(selectedSchema.schema_id, schema)
      } else {
        // Create new
        await api.createSchema(schema)
      }

      await loadSchemas()
      setView('list')
      setSelectedSchema(undefined)
    } catch (error: any) {
      throw new Error(error.message)
    }
  }

  const handleEdit = (schema: CustomSchema) => {
    setSelectedSchema(schema)
    setView('edit')
  }

  const handleDelete = async (schemaId: string) => {
    await loadSchemas()
  }

  const handleCancel = () => {
    setView('list')
    setSelectedSchema(undefined)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        {view === 'list' ? (
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Schemas Personalizados</h1>
                <p className="text-gray-600 mt-1">
                  {selectedTema
                    ? `Schemas para el tema: ${selectedTema}`
                    : 'Todos los schemas disponibles'}
                </p>
              </div>
              <Button onClick={() => setView('create')}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Nuevo Schema
              </Button>
            </div>
          </div>
        ) : (
          <div className="mb-6">
            <Button variant="ghost" onClick={handleCancel} className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver a la lista
            </Button>
          </div>
        )}

        {/* Content */}
        <div className="bg-white rounded-lg border p-6">
          {loading && view === 'list' ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Cargando schemas...</p>
            </div>
          ) : view === 'list' ? (
            <SchemaList
              schemas={schemas}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onRefresh={loadSchemas}
            />
          ) : (
            <SchemaBuilder
              initialSchema={selectedSchema}
              tema={selectedTema || undefined}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          )}
        </div>
      </div>
    </div>
  )
}
