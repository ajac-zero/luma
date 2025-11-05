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
import { Textarea } from './ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Switch } from './ui/switch'
import { AlertCircle, Loader2, Settings, Sparkles } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

interface ChunkingConfigModalProps {
  isOpen: boolean
  onClose: () => void
  fileName: string
  tema: string
  collectionName: string
  onPreview: (config: ChunkingConfig) => void
}

export interface ChunkingConfig {
  file_name: string
  tema: string
  collection_name: string
  max_tokens: number
  target_tokens: number
  chunk_size: number
  chunk_overlap: number
  use_llm: boolean
  custom_instructions: string
}

interface ChunkingProfile {
  id: string
  name: string
  description: string
  max_tokens: number
  target_tokens: number
  chunk_size: number
  chunk_overlap: number
  use_llm: boolean
}

export function ChunkingConfigModal({
  isOpen,
  onClose,
  fileName,
  tema,
  collectionName,
  onPreview,
}: ChunkingConfigModalProps) {
  const [profiles, setProfiles] = useState<ChunkingProfile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('balanced')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Custom configuration
  const [maxTokens, setMaxTokens] = useState(950)
  const [targetTokens, setTargetTokens] = useState(800)
  const [chunkSize, setChunkSize] = useState(1000)
  const [chunkOverlap, setChunkOverlap] = useState(200)
  const [useLLM, setUseLLM] = useState(true)
  const [customInstructions, setCustomInstructions] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadProfiles()
    }
  }, [isOpen])

  const loadProfiles = async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await api.getChunkingProfiles()
      setProfiles(result.profiles)
    } catch (err) {
      console.error('Error loading profiles:', err)
      setError(err instanceof Error ? err.message : 'Error cargando perfiles')
    } finally {
      setLoading(false)
    }
  }

  const handleProfileChange = (profileId: string) => {
    setSelectedProfile(profileId)
    const profile = profiles.find((p) => p.id === profileId)
    if (profile) {
      setMaxTokens(profile.max_tokens)
      setTargetTokens(profile.target_tokens)
      setChunkSize(profile.chunk_size)
      setChunkOverlap(profile.chunk_overlap)
      setUseLLM(profile.use_llm)
    }
  }

  const handlePreview = () => {
    const config: ChunkingConfig = {
      file_name: fileName,
      tema: tema,
      collection_name: collectionName,
      max_tokens: maxTokens,
      target_tokens: targetTokens,
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
      use_llm: useLLM,
      custom_instructions: useLLM ? customInstructions : '',
    }
    onPreview(config)
  }

  const handleClose = () => {
    setError(null)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configurar Chunking
          </DialogTitle>
          <DialogDescription>
            Configura cómo se procesará el archivo <strong>{fileName}</strong>
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-500">Cargando perfiles...</span>
          </div>
        ) : error ? (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-4 rounded">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        ) : (
          <Tabs defaultValue="profiles" className="flex-1">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="profiles">Perfiles</TabsTrigger>
              <TabsTrigger value="custom">Personalizado</TabsTrigger>
            </TabsList>

            {/* Tab de Perfiles */}
            <TabsContent value="profiles" className="space-y-4">
              <div className="space-y-2">
                <Label>Perfil de Configuración</Label>
                <Select value={selectedProfile} onValueChange={handleProfileChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona un perfil" />
                  </SelectTrigger>
                  <SelectContent>
                    {profiles.map((profile) => (
                      <SelectItem key={profile.id} value={profile.id}>
                        <div className="flex flex-col">
                          <span className="font-medium">{profile.name}</span>
                          <span className="text-xs text-gray-500">{profile.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Mostrar detalles del perfil seleccionado */}
              {selectedProfile && (
                <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="font-medium">Max Tokens:</span> {maxTokens}
                    </div>
                    <div>
                      <span className="font-medium">Target Tokens:</span> {targetTokens}
                    </div>
                    <div>
                      <span className="font-medium">Chunk Size:</span> {chunkSize}
                    </div>
                    <div>
                      <span className="font-medium">Overlap:</span> {chunkOverlap}
                    </div>
                    <div className="col-span-2">
                      <span className="font-medium">LLM:</span>{' '}
                      {useLLM ? '✅ Habilitado' : '❌ Deshabilitado'}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* Tab Personalizado */}
            <TabsContent value="custom" className="space-y-4 overflow-y-auto max-h-[50vh]">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxTokens">Max Tokens</Label>
                  <Input
                    id="maxTokens"
                    type="number"
                    min={100}
                    max={2000}
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(Number(e.target.value))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="targetTokens">Target Tokens</Label>
                  <Input
                    id="targetTokens"
                    type="number"
                    min={100}
                    max={2000}
                    value={targetTokens}
                    onChange={(e) => setTargetTokens(Number(e.target.value))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="chunkSize">Chunk Size</Label>
                  <Input
                    id="chunkSize"
                    type="number"
                    min={100}
                    max={3000}
                    value={chunkSize}
                    onChange={(e) => setChunkSize(Number(e.target.value))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="chunkOverlap">Chunk Overlap</Label>
                  <Input
                    id="chunkOverlap"
                    type="number"
                    min={0}
                    max={1000}
                    value={chunkOverlap}
                    onChange={(e) => setChunkOverlap(Number(e.target.value))}
                  />
                </div>
              </div>

              {/* Toggle LLM */}
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <div>
                    <Label htmlFor="useLLM" className="font-medium cursor-pointer">
                      Usar LLM (Gemini)
                    </Label>
                    <p className="text-xs text-gray-600">
                      Procesamiento inteligente con IA
                    </p>
                  </div>
                </div>
                <Switch
                  id="useLLM"
                  checked={useLLM}
                  onCheckedChange={setUseLLM}
                />
              </div>

              {/* Custom Instructions (solo si LLM está habilitado) */}
              {useLLM && (
                <div className="space-y-2">
                  <Label htmlFor="customInstructions">
                    Instrucciones Personalizadas (Opcional)
                  </Label>
                  <Textarea
                    id="customInstructions"
                    placeholder="Ej: Mantén todos los términos técnicos en inglés..."
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    rows={3}
                  />
                  <p className="text-xs text-gray-500">
                    Instrucciones adicionales para guiar el procesamiento con IA
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}

        <DialogFooter className="flex justify-between items-center pt-4 border-t">
          <Button variant="outline" onClick={handleClose}>
            Cancelar
          </Button>
          <Button onClick={handlePreview} disabled={loading}>
            Generar Preview
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
