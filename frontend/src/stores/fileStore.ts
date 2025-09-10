import { create } from 'zustand'

interface FileData {
  name: string
  full_path: string
  tema: string
  size: number
  last_modified: string
  content_type?: string
  url?: string
}

interface FileStore {
  // Estado
  selectedTema: string | null
  files: FileData[]
  temas: string[]
  loading: boolean
  selectedFiles: Set<string>
  
  // Acciones
  setSelectedTema: (tema: string | null) => void
  setFiles: (files: FileData[]) => void
  setTemas: (temas: string[]) => void
  setLoading: (loading: boolean) => void
  toggleFileSelection: (filename: string) => void
  selectAllFiles: () => void
  clearSelection: () => void
}

export const useFileStore = create<FileStore>((set) => ({
  // Estado inicial
  selectedTema: null,
  files: [],
  temas: [],
  loading: false,
  selectedFiles: new Set(),

  // Acciones
  setSelectedTema: (tema) => set({ selectedTema: tema }),
  setFiles: (files) => set({ files }),
  setTemas: (temas) => set({ temas }),
  setLoading: (loading) => set({ loading }),
  
  toggleFileSelection: (filename) => set((state) => {
    const newSelection = new Set(state.selectedFiles)
    if (newSelection.has(filename)) {
      newSelection.delete(filename)
    } else {
      newSelection.add(filename)
    }
    return { selectedFiles: newSelection }
  }),
  
  selectAllFiles: () => set((state) => ({
    selectedFiles: new Set(state.files.map(f => f.name))
  })),
  
  clearSelection: () => set({ selectedFiles: new Set() }),
}))