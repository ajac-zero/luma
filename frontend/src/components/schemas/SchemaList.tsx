/**
 * Schema List Component
 * Lista y gestiona schemas existentes
 */
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Trash2, Edit, Globe, FolderClosed } from 'lucide-react'
import type { CustomSchema } from '@/types/schema'
import { api } from '@/services/api'

interface SchemaListProps {
  schemas: CustomSchema[]
  onEdit: (schema: CustomSchema) => void
  onDelete: (schemaId: string) => void
  onRefresh: () => void
}

export function SchemaList({ schemas, onEdit, onDelete, onRefresh }: SchemaListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (schema: CustomSchema) => {
    if (!schema.schema_id) return

    const confirmed = window.confirm(
      `¿Estás seguro de eliminar el schema "${schema.schema_name}"?\n\nEsta acción no se puede deshacer.`
    )

    if (!confirmed) return

    setDeletingId(schema.schema_id)
    try {
      await api.deleteSchema(schema.schema_id)
      onDelete(schema.schema_id)
    } catch (error: any) {
      alert(`Error eliminando schema: ${error.message}`)
    } finally {
      setDeletingId(null)
    }
  }

  if (schemas.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed">
        <p className="text-gray-600 mb-2">No hay schemas creados</p>
        <p className="text-sm text-gray-500">Crea tu primer schema para empezar</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {schemas.map((schema) => (
        <SchemaCard
          key={schema.schema_id}
          schema={schema}
          onEdit={() => onEdit(schema)}
          onDelete={() => handleDelete(schema)}
          isDeleting={deletingId === schema.schema_id}
        />
      ))}
    </div>
  )
}

function SchemaCard({
  schema,
  onEdit,
  onDelete,
  isDeleting
}: {
  schema: CustomSchema
  onEdit: () => void
  onDelete: () => void
  isDeleting: boolean
}) {
  return (
    <div className="p-4 bg-white rounded-lg border hover:border-blue-300 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold">{schema.schema_name}</h3>
            {schema.is_global ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                <Globe className="h-3 w-3" />
                Global
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-full">
                <FolderClosed className="h-3 w-3" />
                {schema.tema}
              </span>
            )}
          </div>

          {/* Description */}
          <p className="text-sm text-gray-600 mb-3">{schema.description}</p>

          {/* Fields Summary */}
          <div className="flex flex-wrap gap-2">
            {schema.fields.slice(0, 5).map((field, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-1 bg-gray-50 text-gray-700 text-xs rounded border"
              >
                <span className="font-medium">{field.name}</span>
                <span className="text-gray-500 ml-1">({field.type})</span>
                {field.required && (
                  <span className="ml-1 text-red-500">*</span>
                )}
              </span>
            ))}
            {schema.fields.length > 5 && (
              <span className="inline-flex items-center px-2 py-1 text-gray-500 text-xs">
                +{schema.fields.length - 5} más
              </span>
            )}
          </div>

          {/* Metadata */}
          {schema.created_at && (
            <p className="text-xs text-gray-500 mt-2">
              Creado: {new Date(schema.created_at).toLocaleDateString('es-ES')}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 ml-4">
          <Button
            variant="outline"
            size="sm"
            onClick={onEdit}
            disabled={isDeleting}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onDelete}
            disabled={isDeleting}
            className="text-red-600 hover:bg-red-50 hover:text-red-700"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
