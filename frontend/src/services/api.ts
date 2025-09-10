const API_BASE_URL = 'http://localhost:8000/api/v1'

interface FileUploadResponse {
  success: boolean
  message: string
  file?: {
    name: string
    full_path: string
    tema: string
    size: number
    last_modified: string
    url?: string
  }
}

interface FileListResponse {
  files: Array<{
    name: string
    full_path: string
    tema: string
    size: number
    last_modified: string
    content_type?: string
  }>
  total: number
  tema?: string
}

interface TemasResponse {
  temas: string[]
  total: number
}

// API calls
export const api = {
  // Obtener todos los temas
  getTemas: async (): Promise<TemasResponse> => {
    const response = await fetch(`${API_BASE_URL}/files/temas`)
    if (!response.ok) throw new Error('Error fetching temas')
    return response.json()
  },

  // Obtener archivos (todos o por tema)
  getFiles: async (tema?: string): Promise<FileListResponse> => {
    const url = tema 
      ? `${API_BASE_URL}/files/?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/`
    
    const response = await fetch(url)
    if (!response.ok) throw new Error('Error fetching files')
    return response.json()
  },

  // Subir archivo
  uploadFile: async (file: File, tema?: string): Promise<FileUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    if (tema) formData.append('tema', tema)

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) throw new Error('Error uploading file')
    return response.json()
  },

  // Eliminar archivo
  deleteFile: async (filename: string, tema?: string): Promise<void> => {
    const url = tema 
      ? `${API_BASE_URL}/files/${encodeURIComponent(filename)}?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/${encodeURIComponent(filename)}`
    
    const response = await fetch(url, { method: 'DELETE' })
    if (!response.ok) throw new Error('Error deleting file')
  },

  // Eliminar múltiples archivos
  deleteFiles: async (filenames: string[], tema?: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/delete-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: filenames,
        tema: tema
      }),
    })
    
    if (!response.ok) throw new Error('Error deleting files')
  },

   // Eliminar tema completo
  deleteTema: async (tema: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/tema/${encodeURIComponent(tema)}/delete-all`, {
      method: 'DELETE'
    })
    
    if (!response.ok) throw new Error('Error deleting tema')
  },

   // Descargar archivo individual
  downloadFile: async (filename: string, tema?: string): Promise<void> => {
    const url = tema 
      ? `${API_BASE_URL}/files/${encodeURIComponent(filename)}/download?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/${encodeURIComponent(filename)}/download`
    
    const response = await fetch(url)
    if (!response.ok) throw new Error('Error downloading file')
    
    // Crear blob y descargar
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },

  // Descargar múltiples archivos como ZIP
  downloadMultipleFiles: async (filenames: string[], tema?: string, zipName?: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/download-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: filenames,
        tema: tema,
        zip_name: zipName || 'archivos'
      }),
    })
    
    if (!response.ok) throw new Error('Error downloading files')
    
    // Crear blob y descargar ZIP
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    
    // Obtener nombre del archivo del header Content-Disposition
    const contentDisposition = response.headers.get('Content-Disposition')
    const filename = contentDisposition?.split('filename=')[1]?.replace(/"/g, '') || 'archivos.zip'
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },

  // Descargar tema completo
  downloadTema: async (tema: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/tema/${encodeURIComponent(tema)}/download-all`)
    if (!response.ok) throw new Error('Error downloading tema')
    
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    
    const contentDisposition = response.headers.get('Content-Disposition')
    const filename = contentDisposition?.split('filename=')[1]?.replace(/"/g, '') || `${tema}.zip`
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  },

}