// Tipos que coinciden con tu backend
export interface FileInfo {
  name: string
  full_path: string
  tema: string
  size: number
  last_modified: string
  content_type?: string
  url?: string
}

export interface FileListResponse {
  files: FileInfo[]
  total: number
  tema?: string
}

export interface FileUploadResponse {
  success: boolean
  message: string
  file?: FileInfo
}

export interface TemasResponse {
  temas: string[]
  total: number
}

export interface FileConflictResponse {
  conflict: boolean
  message: string
  existing_file: string
  suggested_name: string
  tema?: string
}