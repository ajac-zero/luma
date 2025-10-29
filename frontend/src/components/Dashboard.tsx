import { useEffect, useState } from 'react'
import { useFileStore } from '@/stores/fileStore'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { Checkbox } from '@/components/ui/checkbox'
import { FileUpload } from './FileUpload'
import { DeleteConfirmDialog } from './DeleteConfirmDialog'
import { PDFPreviewModal } from './PDFPreviewModal'
import {
  Upload,
  Download,
  Trash2,
  Search,
  FileText,
  Eye,
  MessageSquare
} from 'lucide-react'

export function Dashboard() {
  const {
    selectedTema,
    files,
    setFiles,
    loading,
    setLoading,
    selectedFiles,
    toggleFileSelection,
    selectAllFiles,
    clearSelection
  } = useFileStore()

  const [searchTerm, setSearchTerm] = useState('')
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [fileToDelete, setFileToDelete] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [downloading, setDownloading] = useState(false)

  // Estados para el modal de preview de PDF
  const [previewModalOpen, setPreviewModalOpen] = useState(false)
  const [previewFileUrl, setPreviewFileUrl] = useState<string | null>(null)
  const [previewFileName, setPreviewFileName] = useState('')
  const [previewFileTema, setPreviewFileTema] = useState<string | undefined>(undefined)
  const [loadingPreview, setLoadingPreview] = useState(false)

  useEffect(() => {
    loadFiles()
  }, [selectedTema])

  const loadFiles = async () => {
    try {
      setLoading(true)
      const response = await api.getFiles(selectedTema || undefined)
      setFiles(response.files)
    } catch (error) {
      console.error('Error loading files:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = () => {
    loadFiles()
  }

  // Eliminar archivo individual
  const handleDeleteSingle = async (filename: string) => {
    setFileToDelete(filename)
    setDeleteDialogOpen(true)
  }

  // Eliminar archivos seleccionados
  const handleDeleteMultiple = () => {
    if (selectedFiles.size === 0) return
    setFileToDelete(null)
    setDeleteDialogOpen(true)
  }

  // Confirmar eliminación
  const confirmDelete = async () => {
    if (!fileToDelete && selectedFiles.size === 0) return

    setDeleting(true)
    try {
      if (fileToDelete) {
        // Eliminar archivo individual
        await api.deleteFile(fileToDelete, selectedTema || undefined)
      } else {
        // Eliminar archivos seleccionados
        const filesToDelete = Array.from(selectedFiles)
        await api.deleteFiles(filesToDelete, selectedTema || undefined)
        clearSelection()
      }

      // Recargar archivos
      await loadFiles()
      setDeleteDialogOpen(false)
      setFileToDelete(null)
    } catch (error) {
      console.error('Error deleting files:', error)
    } finally {
      setDeleting(false)
    }
  }

  // Descargar archivo individual
  const handleDownloadSingle = async (filename: string) => {
    try {
      setDownloading(true)
      await api.downloadFile(filename, selectedTema || undefined)
    } catch (error) {
      console.error('Error downloading file:', error)
    } finally {
      setDownloading(false)
    }
  }

  // Descargar archivos seleccionados
  const handleDownloadMultiple = async () => {
    if (selectedFiles.size === 0) return

    try {
      setDownloading(true)
      const filesToDownload = Array.from(selectedFiles)
      const zipName = selectedTema ? `${selectedTema}_archivos` : 'archivos_seleccionados'
      await api.downloadMultipleFiles(filesToDownload, selectedTema || undefined, zipName)
    } catch (error) {
      console.error('Error downloading files:', error)
    } finally {
      setDownloading(false)
    }
  }

  // Abrir preview de PDF
  const handlePreviewFile = async (filename: string, tema?: string) => {
    // Solo permitir preview de archivos PDF
    if (!filename.toLowerCase().endsWith('.pdf')) {
      console.log('Solo se pueden previsualizar archivos PDF')
      return
    }

    try {
      setLoadingPreview(true)
      setPreviewFileName(filename)
      setPreviewFileTema(tema)

      // Obtener la URL temporal (SAS) para el archivo
      const url = await api.getPreviewUrl(filename, tema)

      setPreviewFileUrl(url)
      setPreviewModalOpen(true)
    } catch (error) {
      console.error('Error obteniendo URL de preview:', error)
      alert('Error al cargar la vista previa del archivo')
    } finally {
      setLoadingPreview(false)
    }
  }

  // Manejar descarga desde el modal de preview
  const handleDownloadFromPreview = async () => {
    if (previewFileName) {
      await handleDownloadSingle(previewFileName)
    }
  }

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Preparar datos para el modal de confirmación
  const getDeleteDialogProps = () => {
    if (fileToDelete) {
      return {
        title: 'Eliminar archivo',
        description: `¿Estás seguro de que quieres eliminar "${fileToDelete}"? Esta acción no se puede deshacer.`,
        fileList: [fileToDelete]
      }
    } else {
      const filesToDelete = Array.from(selectedFiles)
      return {
        title: `Eliminar ${filesToDelete.length} archivos`,
        description: `¿Estás seguro de que quieres eliminar ${filesToDelete.length} archivo${filesToDelete.length !== 1 ? 's' : ''}? Esta acción no se puede deshacer.`,
        fileList: filesToDelete
      }
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">
              {selectedTema ? `Tema: ${selectedTema}` : 'Todos los archivos'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {filteredFiles.length} archivo{filteredFiles.length !== 1 ? 's' : ''}
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button onClick={() => setUploadDialogOpen(true)}>
              <Upload className="w-4 h-4 mr-2" />
              Subir archivo
            </Button>
          </div>
        </div>

        {/* Search and Actions */}
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Buscar archivos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {selectedFiles.size > 0 && (
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleDownloadMultiple}
                disabled={downloading}
              >
                <Download className="w-4 h-4 mr-2" />
                {downloading ? 'Descargando...' : `Descargar (${selectedFiles.size})`}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleDeleteMultiple}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Eliminar ({selectedFiles.size})
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500">Cargando archivos...</p>
          </div>
        ) : filteredFiles.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <FileText className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-500">
              {searchTerm ? 'No se encontraron archivos' : 'No hay archivos en este tema'}
            </p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={selectedFiles.size === filteredFiles.length && filteredFiles.length > 0}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        selectAllFiles()
                      } else {
                        clearSelection()
                      }
                    }}
                  />
                </TableHead>
                <TableHead>Nombre</TableHead>
                <TableHead>Tamaño</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Tema</TableHead>
                <TableHead className="w-32">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredFiles.map((file) => {
                const isPDF = file.name.toLowerCase().endsWith('.pdf')

                return (
                  <TableRow key={file.full_path}>
                    <TableCell>
                      <Checkbox
                        checked={selectedFiles.has(file.name)}
                        onCheckedChange={() => toggleFileSelection(file.name)}
                      />
                    </TableCell>
                    <TableCell className="font-medium">
                      {isPDF ? (
                        <button
                          onClick={() => handlePreviewFile(file.name, file.tema || undefined)}
                          className="text-blue-600 hover:text-blue-800 hover:underline text-left transition-colors"
                          disabled={loadingPreview}
                        >
                          {file.name}
                        </button>
                      ) : (
                        <span>{file.name}</span>
                      )}
                    </TableCell>
                    <TableCell>{formatFileSize(file.size)}</TableCell>
                    <TableCell>{formatDate(file.last_modified)}</TableCell>
                    <TableCell>
                      <span className="px-2 py-1 bg-gray-100 rounded-md text-sm">
                        {file.tema || 'General'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadSingle(file.name)}
                          disabled={downloading}
                          title="Descargar archivo"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Ver chunks"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Generar preguntas"
                        >
                          <MessageSquare className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteSingle(file.name)}
                          title="Eliminar archivo"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </div>

      {/* Upload Dialog */}
      <FileUpload 
        open={uploadDialogOpen} 
        onOpenChange={setUploadDialogOpen}
        onSuccess={handleUploadSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={confirmDelete}
        loading={deleting}
        {...getDeleteDialogProps()}
      />

      {/* PDF Preview Modal */}
      <PDFPreviewModal
        open={previewModalOpen}
        onOpenChange={setPreviewModalOpen}
        fileUrl={previewFileUrl}
        fileName={previewFileName}
        onDownload={handleDownloadFromPreview}
      />
    </div>
  )
}