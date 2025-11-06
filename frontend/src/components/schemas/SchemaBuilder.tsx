/**
 * Schema Builder Component
 * Permite crear y editar schemas personalizados desde el frontend
 */
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Trash2, Plus, AlertCircle, CheckCircle2 } from 'lucide-react'
import type { CustomSchema, SchemaField, FieldType, FieldTypeOption } from '@/types/schema'
import { FIELD_TYPE_OPTIONS } from '@/types/schema'

interface SchemaBuilderProps {
  initialSchema?: CustomSchema
  tema?: string
  onSave: (schema: CustomSchema) => Promise<void>
  onCancel?: () => void
}

export function SchemaBuilder({ initialSchema, tema, onSave, onCancel }: SchemaBuilderProps) {
  const [schema, setSchema] = useState<CustomSchema>(
    initialSchema || {
      schema_name: '',
      description: '',
      fields: [],
      tema: tema,
      is_global: false
    }
  )

  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addField = () => {
    setSchema({
      ...schema,
      fields: [
        ...schema.fields,
        {
          name: '',
          type: 'string',
          description: '',
          required: false
        }
      ]
    })
  }

  const updateField = (index: number, updates: Partial<SchemaField>) => {
    const newFields = [...schema.fields]
    newFields[index] = { ...newFields[index], ...updates }
    setSchema({ ...schema, fields: newFields })
  }

  const removeField = (index: number) => {
    setSchema({
      ...schema,
      fields: schema.fields.filter((_, i) => i !== index)
    })
  }

  const handleSave = async () => {
    setError(null)

    // Validaciones básicas
    if (!schema.schema_name.trim()) {
      setError('El nombre del schema es requerido')
      return
    }

    if (!schema.description.trim()) {
      setError('La descripción es requerida')
      return
    }

    if (schema.fields.length === 0) {
      setError('Debe agregar al menos un campo')
      return
    }

    // Validar campos
    for (let i = 0; i < schema.fields.length; i++) {
      const field = schema.fields[i]
      if (!field.name.trim()) {
        setError(`El campo ${i + 1} necesita un nombre`)
        return
      }
      if (!field.description.trim()) {
        setError(`El campo "${field.name}" necesita una descripción`)
        return
      }
    }

    setSaving(true)
    try {
      await onSave(schema)
    } catch (err: any) {
      setError(err.message || 'Error guardando schema')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">
          {initialSchema ? 'Editar Schema' : 'Crear Nuevo Schema'}
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Define los campos que quieres extraer de los documentos
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Basic Info */}
      <div className="space-y-4 p-6 bg-white rounded-lg border">
        <div>
          <Label htmlFor="schema_name">Nombre del Schema *</Label>
          <Input
            id="schema_name"
            value={schema.schema_name}
            onChange={(e) => setSchema({ ...schema, schema_name: e.target.value })}
            placeholder="Ej: Contrato Legal, Factura Comercial"
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="description">Descripción *</Label>
          <Input
            id="description"
            value={schema.description}
            onChange={(e) => setSchema({ ...schema, description: e.target.value })}
            placeholder="¿Qué información extrae este schema?"
            className="mt-1"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_global"
            checked={schema.is_global}
            onChange={(e) => setSchema({ ...schema, is_global: e.target.checked })}
            className="rounded"
          />
          <Label htmlFor="is_global" className="cursor-pointer">
            Disponible para todos los temas (global)
          </Label>
        </div>

        {!schema.is_global && (
          <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded">
            Este schema solo estará disponible para el tema: <strong>{tema || 'actual'}</strong>
          </div>
        )}
      </div>

      {/* Fields */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Campos a Extraer</h3>
            <p className="text-sm text-gray-600">Define qué datos quieres que la IA extraiga</p>
          </div>
          <Button onClick={addField} size="sm" variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            Agregar Campo
          </Button>
        </div>

        {schema.fields.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed">
            <p className="text-gray-600 mb-3">No hay campos definidos</p>
            <Button onClick={addField} variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Agregar Primer Campo
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {schema.fields.map((field, index) => (
              <SchemaFieldRow
                key={index}
                field={field}
                index={index}
                onUpdate={(updates) => updateField(index, updates)}
                onRemove={() => removeField(index)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-3 justify-end pt-4 border-t">
        {onCancel && (
          <Button variant="outline" onClick={onCancel} disabled={saving}>
            Cancelar
          </Button>
        )}
        <Button onClick={handleSave} disabled={saving}>
          {saving ? (
            <>Guardando...</>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Guardar Schema
            </>
          )}
        </Button>
      </div>
    </div>
  )
}

function SchemaFieldRow({
  field,
  index,
  onUpdate,
  onRemove
}: {
  field: SchemaField
  index: number
  onUpdate: (updates: Partial<SchemaField>) => void
  onRemove: () => void
}) {
  const selectedTypeOption = FIELD_TYPE_OPTIONS.find(opt => opt.value === field.type)

  return (
    <div className="p-4 bg-white rounded-lg border hover:border-blue-300 transition-colors">
      <div className="grid grid-cols-12 gap-3 items-start">
        {/* Field Number */}
        <div className="col-span-1 flex items-center justify-center">
          <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-semibold flex items-center justify-center text-sm">
            {index + 1}
          </div>
        </div>

        {/* Field Name */}
        <div className="col-span-3">
          <Label className="text-xs text-gray-600">Nombre del campo *</Label>
          <Input
            value={field.name}
            onChange={(e) => onUpdate({ name: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
            placeholder="nombre_campo"
            className="mt-1"
          />
        </div>

        {/* Field Type */}
        <div className="col-span-2">
          <Label className="text-xs text-gray-600">Tipo *</Label>
          <select
            value={field.type}
            onChange={(e) => onUpdate({ type: e.target.value as FieldType })}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            {FIELD_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Description */}
        <div className="col-span-4">
          <Label className="text-xs text-gray-600">Descripción para IA *</Label>
          <Input
            value={field.description}
            onChange={(e) => onUpdate({ description: e.target.value })}
            placeholder="¿Qué debe extraer la IA?"
            className="mt-1"
          />
        </div>

        {/* Required Checkbox */}
        <div className="col-span-1 flex items-end pb-2">
          <label className="flex items-center gap-1 text-xs cursor-pointer">
            <input
              type="checkbox"
              checked={field.required}
              onChange={(e) => onUpdate({ required: e.target.checked })}
              className="rounded"
            />
            <span>Requerido</span>
          </label>
        </div>

        {/* Delete Button */}
        <div className="col-span-1 flex items-end justify-center pb-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onRemove}
            className="text-red-600 hover:bg-red-50 hover:text-red-700"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Min/Max Values (for numeric types) */}
      {selectedTypeOption?.supportsMinMax && (
        <div className="mt-3 pt-3 border-t grid grid-cols-2 gap-3 ml-12">
          <div>
            <Label className="text-xs text-gray-600">Valor Mínimo (opcional)</Label>
            <Input
              type="number"
              value={field.min_value ?? ''}
              onChange={(e) => onUpdate({ min_value: e.target.value ? parseFloat(e.target.value) : undefined })}
              placeholder="Sin límite"
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-gray-600">Valor Máximo (opcional)</Label>
            <Input
              type="number"
              value={field.max_value ?? ''}
              onChange={(e) => onUpdate({ max_value: e.target.value ? parseFloat(e.target.value) : undefined })}
              placeholder="Sin límite"
              className="mt-1"
            />
          </div>
        </div>
      )}
    </div>
  )
}
