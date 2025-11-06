/**
 * Chunking Config Modal con LandingAI
 * Reemplaza el modal anterior, ahora usa LandingAI con modos flexible y schemas
 */
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
import { Label } from './ui/label'
import { Input } from './ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { AlertCircle, Loader2, Settings, Zap, Target, FileText, Table2, Image } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import type { CustomSchema } from '@/types/schema'

interface ChunkingConfigModalProps {
  isOpen: boolean
  onClose: () => void
  fileName: string
  tema: string
  collectionName: string
  onProcess: (config: LandingAIConfig) => void
}

export interface LandingAIConfig {
  file_name: string
  tema: string
  collection_name: string
  mode: 'quick' | 'extract'
  schema_id?: string
  include_chunk_types: string[]
  max_tokens_per_chunk: number
  merge_small_chunks: boolean
}

export function ChunkingConfigModalLandingAI({
  isOpen,
  onClose,
  fileName,
  tema,
  collectionName,
  onProcess,
}: ChunkingConfigModalProps) {
  const [mode, setMode] = useState<'quick' | 'extract'>('quick')
  const [schemas, setSchemas] = useState<CustomSchema[]>([])
  const [selectedSchema, setSelectedSchema] = useState<string | undefined>()
  const [chunkTypes, setChunkTypes] = useState<string[]>(['text', 'table'])
  const [maxTokens, setMaxTokens] = useState(1500)
  const [mergeSmall, setMergeSmall] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadSchemas()
    }
  }, [isOpen, tema])

  const loadSchemas = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.listSchemas(tema)
      setSchemas(data)
    } catch (err) {
      console.error('Error loading schemas:', err)
      setError(err instanceof Error ? err.message : 'Error cargando schemas')
    } finally {
      setLoading(false)
    }
  }

  const toggleChunkType = (type: string) => {
    if (chunkTypes.includes(type)) {
      setChunkTypes(chunkTypes.filter(t => t !== type))
    } else {
      setChunkTypes([...chunkTypes, type])
    }
  }

  const handleProcess = () => {
    if (mode === 'extract' && !selectedSchema) {
      setError('Debes seleccionar un schema en modo extracción')
      return
    }

    if (chunkTypes.length === 0) {
      setError('Debes seleccionar al menos un tipo de contenido')
      return
    }

    const config: LandingAIConfig = {
      file_name: fileName,
      tema: tema,
      collection_name: collectionName,
      mode: mode,
      schema_id: selectedSchema,
      include_chunk_types: chunkTypes,
      max_tokens_per_chunk: maxTokens,
      merge_small_chunks: mergeSmall,
    }

    onProcess(config)
  }

  const handleClose = () => {
    setError(null)
    onClose()
  }

  const selectedSchemaData = schemas.find(s => s.schema_id === selectedSchema)

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configurar Procesamiento con LandingAI
          </DialogTitle>
          <DialogDescription>
            Configura cómo se procesará <strong>{fileName}</strong> usando LandingAI Document AI
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-4 rounded">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-6 flex-1 overflow-y-auto">
          {/* Modo de Procesamiento */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Modo de Procesamiento</Label>
            <div className="grid grid-cols-2 gap-4">
              <ModeCard
                icon={<Zap className="h-6 w-6" />}
                title="Rápido"
                description="Solo extracción de texto sin análisis estructurado"
                time="~5-10 seg"
                selected={mode === 'quick'}
                onClick={() => setMode('quick')}
              />
              <ModeCard
                icon={<Target className="h-6 w-6" />}
                title="Con Extracción"
                description="Parse + extracción de datos estructurados con schema"
                time="~15-30 seg"
                selected={mode === 'extract'}
                onClick={() => setMode('extract')}
              />
            </div>
          </div>

          {/* Schema Selector (solo en modo extract) */}
          {mode === 'extract' && (
            <div className="space-y-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <Label className="text-base font-semibold">Schema a Usar</Label>
              {loading ? (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Cargando schemas...</span>
                </div>
              ) : schemas.length === 0 ? (
                <div className="text-sm text-gray-600">
                  <p>No hay schemas disponibles para este tema.</p>
                  <p className="mt-1">Crea uno primero en la sección de Schemas.</p>
                </div>
              ) : (
                <>
                  <Select value={selectedSchema} onValueChange={setSelectedSchema}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona un schema..." />
                    </SelectTrigger>
                    <SelectContent>
                      {schemas.map((schema) => (
                        <SelectItem key={schema.schema_id} value={schema.schema_id!}>
                          <div className="flex flex-col">
                            <span className="font-medium">{schema.schema_name}</span>
                            <span className="text-xs text-gray-500">{schema.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Preview del schema seleccionado */}
                  {selectedSchemaData && (
                    <div className="mt-3 p-3 bg-white rounded border">
                      <p className="text-sm font-medium mb-2">Campos a extraer:</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedSchemaData.fields.map((field, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                          >
                            {field.name}
                            {field.required && <span className="ml-1 text-red-500">*</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* Tipos de Contenido */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Tipos de Contenido a Incluir</Label>
            <div className="grid grid-cols-3 gap-3">
              <ChunkTypeOption
                icon={<FileText className="h-5 w-5" />}
                label="Texto"
                selected={chunkTypes.includes('text')}
                onClick={() => toggleChunkType('text')}
              />
              <ChunkTypeOption
                icon={<Table2 className="h-5 w-5" />}
                label="Tablas"
                selected={chunkTypes.includes('table')}
                onClick={() => toggleChunkType('table')}
              />
              <ChunkTypeOption
                icon={<Image className="h-5 w-5" />}
                label="Figuras"
                selected={chunkTypes.includes('figure')}
                onClick={() => toggleChunkType('figure')}
              />
            </div>
          </div>

          {/* Configuración Avanzada */}
          <details className="border rounded-lg">
            <summary className="px-4 py-3 cursor-pointer font-medium hover:bg-gray-50">
              Configuración Avanzada
            </summary>
            <div className="p-4 space-y-4 border-t">
              <div className="space-y-2">
                <Label htmlFor="maxTokens">
                  Tokens máximos por chunk: <strong>{maxTokens}</strong>
                </Label>
                <input
                  id="maxTokens"
                  type="range"
                  min="500"
                  max="3000"
                  step="100"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  Tablas y figuras pueden exceder hasta 50% más
                </p>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="mergeSmall"
                  checked={mergeSmall}
                  onChange={(e) => setMergeSmall(e.target.checked)}
                  className="rounded"
                />
                <Label htmlFor="mergeSmall" className="cursor-pointer">
                  Unir chunks pequeños de la misma página
                </Label>
              </div>
            </div>
          </details>
        </div>

        <DialogFooter className="flex justify-between items-center pt-4 border-t">
          <div className="text-sm text-gray-600">
            Tiempo estimado: <strong>{mode === 'quick' ? '~5-10 seg' : '~15-30 seg'}</strong>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose}>
              Cancelar
            </Button>
            <Button onClick={handleProcess} disabled={loading}>
              Procesar con LandingAI
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function ModeCard({ icon, title, description, time, selected, onClick }: any) {
  return (
    <div
      onClick={onClick}
      className={`
        p-4 border-2 rounded-lg cursor-pointer transition-all
        ${selected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
        }
      `}
    >
      <div className="flex items-center gap-3 mb-2">
        <div className={selected ? 'text-blue-600' : 'text-gray-400'}>
          {icon}
        </div>
        <h4 className="font-semibold">{title}</h4>
      </div>
      <p className="text-sm text-gray-600 mb-1">{description}</p>
      <p className="text-xs text-gray-500">{time}</p>
    </div>
  )
}

function ChunkTypeOption({ icon, label, selected, onClick }: any) {
  return (
    <div
      onClick={onClick}
      className={`
        p-3 border-2 rounded-lg cursor-pointer transition-all text-center
        ${selected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300'
        }
      `}
    >
      <div className={`flex justify-center mb-2 ${selected ? 'text-blue-600' : 'text-gray-400'}`}>
        {icon}
      </div>
      <p className="text-sm font-medium">{label}</p>
    </div>
  )
}
