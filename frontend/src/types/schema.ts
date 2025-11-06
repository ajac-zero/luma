/**
 * Tipos TypeScript para schemas personalizables
 */

export type FieldType =
  | 'string'
  | 'integer'
  | 'float'
  | 'boolean'
  | 'array_string'
  | 'array_integer'
  | 'array_float'
  | 'date'

export interface SchemaField {
  name: string
  type: FieldType
  description: string
  required: boolean
  min_value?: number
  max_value?: number
  pattern?: string
}

export interface CustomSchema {
  schema_id?: string
  schema_name: string
  description: string
  fields: SchemaField[]
  created_at?: string
  updated_at?: string
  tema?: string
  is_global: boolean
}

export interface SchemaValidationResponse {
  valid: boolean
  message: string
  json_schema?: any
  errors?: string[]
}

// Opciones para el selector de tipo
export interface FieldTypeOption {
  value: FieldType
  label: string
  description: string
  supportsMinMax: boolean
}

export const FIELD_TYPE_OPTIONS: FieldTypeOption[] = [
  { value: 'string', label: 'Texto', description: 'Texto simple', supportsMinMax: false },
  { value: 'integer', label: 'Número Entero', description: 'Número sin decimales', supportsMinMax: true },
  { value: 'float', label: 'Número Decimal', description: 'Número con decimales', supportsMinMax: true },
  { value: 'boolean', label: 'Verdadero/Falso', description: 'Sí o No', supportsMinMax: false },
  { value: 'array_string', label: 'Lista de Textos', description: 'Múltiples textos', supportsMinMax: false },
  { value: 'array_integer', label: 'Lista de Números', description: 'Múltiples números enteros', supportsMinMax: true },
  { value: 'array_float', label: 'Lista de Decimales', description: 'Múltiples números decimales', supportsMinMax: true },
  { value: 'date', label: 'Fecha', description: 'Fecha en formato ISO', supportsMinMax: false },
]
