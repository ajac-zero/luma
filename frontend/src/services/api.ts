const API_BASE_URL = "/api/v1";

interface FileUploadResponse {
  success: boolean;
  message: string;
  file?: {
    name: string;
    full_path: string;
    tema: string;
    size: number;
    last_modified: string;
    url?: string;
  };
}

interface FileListResponse {
  files: Array<{
    name: string;
    full_path: string;
    tema: string;
    size: number;
    last_modified: string;
    content_type?: string;
  }>;
  total: number;
  tema?: string;
}

interface TemasResponse {
  temas: string[];
  total: number;
}

interface DataroomsResponse {
  datarooms: Array<{
    name: string;
    collection: string;
    storage: string;
  }>;
}

interface DataroomInfo {
  name: string;
  collection: string;
  storage: string;
  file_count: number;
  total_size_bytes: number;
  total_size_mb: number;
  collection_exists: boolean;
  vector_count: number | null;
  collection_info: {
    vectors_count: number;
    indexed_vectors_count: number;
    points_count: number;
    segments_count: number;
    status: string;
  } | null;
  file_types: Record<string, number>;
  recent_files: Array<{
    name: string;
    size_mb: number;
    last_modified: string;
  }>;
}

interface CreateDataroomRequest {
  name: string;
  collection?: string;
  storage?: string;
}

// API calls
export const api = {
  // Obtener todos los temas (legacy)
  getTemas: async (): Promise<TemasResponse> => {
    const response = await fetch(`${API_BASE_URL}/files/temas`);
    if (!response.ok) throw new Error("Error fetching temas");
    return response.json();
  },

  // Obtener todos los datarooms
  getDatarooms: async (): Promise<DataroomsResponse> => {
    const response = await fetch(`${API_BASE_URL}/dataroom/`);
    if (!response.ok) throw new Error("Error fetching datarooms");
    return response.json();
  },

  // Crear un nuevo dataroom
  createDataroom: async (
    data: CreateDataroomRequest,
  ): Promise<{
    message: string;
    dataroom: {
      name: string;
      collection: string;
      storage: string;
    };
  }> => {
    const response = await fetch(`${API_BASE_URL}/dataroom/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Error creating dataroom");
    return response.json();
  },

  // Eliminar un dataroom
  deleteDataroom: async (
    dataroomName: string,
  ): Promise<{
    message: string;
    dataroom_name: string;
  }> => {
    const response = await fetch(
      `${API_BASE_URL}/dataroom/${encodeURIComponent(dataroomName)}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) throw new Error("Error deleting dataroom");
    return response.json();
  },

  // Obtener información detallada de un dataroom
  getDataroomInfo: async (dataroomName: string): Promise<DataroomInfo> => {
    const response = await fetch(
      `${API_BASE_URL}/dataroom/${encodeURIComponent(dataroomName)}/info`,
    );
    if (!response.ok) throw new Error("Error fetching dataroom info");
    return response.json();
  },

  // Obtener archivos (todos o por tema)
  getFiles: async (tema?: string): Promise<FileListResponse> => {
    const url = tema
      ? `${API_BASE_URL}/files/?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Error fetching files");
    return response.json();
  },

  // Subir archivo
  uploadFile: async (
    file: File,
    tema?: string,
  ): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    if (tema) formData.append("tema", tema);

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Error uploading file");
    return response.json();
  },

  // Eliminar archivo
  deleteFile: async (filename: string, tema?: string): Promise<void> => {
    const url = tema
      ? `${API_BASE_URL}/files/${encodeURIComponent(filename)}?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/${encodeURIComponent(filename)}`;

    const response = await fetch(url, { method: "DELETE" });
    if (!response.ok) throw new Error("Error deleting file");
  },

  // Eliminar múltiples archivos
  deleteFiles: async (filenames: string[], tema?: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/delete-batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        files: filenames,
        tema: tema,
      }),
    });

    if (!response.ok) throw new Error("Error deleting files");
  },

  // Eliminar tema completo
  deleteTema: async (tema: string): Promise<void> => {
    const response = await fetch(
      `${API_BASE_URL}/files/tema/${encodeURIComponent(tema)}/delete-all`,
      {
        method: "DELETE",
      },
    );

    if (!response.ok) throw new Error("Error deleting tema");
  },

  // Descargar archivo individual
  downloadFile: async (filename: string, tema?: string): Promise<void> => {
    const url = tema
      ? `${API_BASE_URL}/files/${encodeURIComponent(filename)}/download?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/${encodeURIComponent(filename)}/download`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Error downloading file");

    // Crear blob y descargar
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Descargar múltiples archivos como ZIP
  downloadMultipleFiles: async (
    filenames: string[],
    tema?: string,
    zipName?: string,
  ): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/files/download-batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        files: filenames,
        tema: tema,
        zip_name: zipName || "archivos",
      }),
    });

    if (!response.ok) throw new Error("Error downloading files");

    // Crear blob y descargar ZIP
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;

    // Obtener nombre del archivo del header Content-Disposition
    const contentDisposition = response.headers.get("Content-Disposition");
    const filename =
      contentDisposition?.split("filename=")[1]?.replace(/"/g, "") ||
      "archivos.zip";

    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Descargar tema completo
  downloadTema: async (tema: string): Promise<void> => {
    const response = await fetch(
      `${API_BASE_URL}/files/tema/${encodeURIComponent(tema)}/download-all`,
    );
    if (!response.ok) throw new Error("Error downloading tema");

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;

    const contentDisposition = response.headers.get("Content-Disposition");
    const filename =
      contentDisposition?.split("filename=")[1]?.replace(/"/g, "") ||
      `${tema}.zip`;

    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Obtener URL temporal para preview de archivos
  getPreviewUrl: async (filename: string, tema?: string): Promise<string> => {
    const url = tema
      ? `${API_BASE_URL}/files/${encodeURIComponent(filename)}/preview-url?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/files/${encodeURIComponent(filename)}/preview-url`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Error getting preview URL");

    const data = await response.json();
    return data.url;
  },

  // ============================================================================
  // Vector Database / Qdrant Operations
  // ============================================================================

  // Health check de la base de datos vectorial
  vectorHealthCheck: async (): Promise<{
    status: string;
    db_type: string;
    message: string;
  }> => {
    const response = await fetch(`${API_BASE_URL}/vectors/health`);
    if (!response.ok) throw new Error("Error checking vector DB health");
    return response.json();
  },

  // Verificar si una colección existe
  checkCollectionExists: async (
    collectionName: string,
  ): Promise<{ exists: boolean; collection_name: string }> => {
    const response = await fetch(`${API_BASE_URL}/vectors/collections/exists`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ collection_name: collectionName }),
    });
    if (!response.ok) throw new Error("Error checking collection");
    return response.json();
  },

  // Crear una nueva colección
  createCollection: async (
    collectionName: string,
    vectorSize: number = 3072,
    distance: string = "Cosine",
  ): Promise<{
    success: boolean;
    collection_name: string;
    message: string;
  }> => {
    const response = await fetch(`${API_BASE_URL}/vectors/collections/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        collection_name: collectionName,
        vector_size: vectorSize,
        distance: distance,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error creating collection");
    }
    return response.json();
  },

  // Eliminar una colección
  deleteCollection: async (
    collectionName: string,
  ): Promise<{
    success: boolean;
    collection_name: string;
    message: string;
  }> => {
    const response = await fetch(
      `${API_BASE_URL}/vectors/collections/${encodeURIComponent(collectionName)}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) throw new Error("Error deleting collection");
    return response.json();
  },

  // Obtener información de una colección
  getCollectionInfo: async (
    collectionName: string,
  ): Promise<{
    name: string;
    vectors_count: number;
    vectors_config: { size: number; distance: string };
    status: string;
  }> => {
    const response = await fetch(
      `${API_BASE_URL}/vectors/collections/${encodeURIComponent(collectionName)}/info`,
    );
    if (!response.ok) throw new Error("Error getting collection info");
    return response.json();
  },

  // Verificar si un archivo existe en una colección
  checkFileExistsInCollection: async (
    collectionName: string,
    fileName: string,
  ): Promise<{
    exists: boolean;
    collection_name: string;
    file_name: string;
    chunk_count?: number;
  }> => {
    const response = await fetch(`${API_BASE_URL}/vectors/files/exists`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        collection_name: collectionName,
        file_name: fileName,
      }),
    });
    if (!response.ok) throw new Error("Error checking file in collection");
    return response.json();
  },

  // Obtener chunks de un archivo
  getChunksByFile: async (
    collectionName: string,
    fileName: string,
    limit?: number,
  ): Promise<{
    collection_name: string;
    file_name: string;
    chunks: Array<{ id: string; payload: any; vector?: number[] }>;
    total_chunks: number;
  }> => {
    const url = limit
      ? `${API_BASE_URL}/vectors/collections/${encodeURIComponent(collectionName)}/files/${encodeURIComponent(fileName)}/chunks?limit=${limit}`
      : `${API_BASE_URL}/vectors/collections/${encodeURIComponent(collectionName)}/files/${encodeURIComponent(fileName)}/chunks`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("Error getting chunks");
    return response.json();
  },

  // Eliminar archivo de colección
  deleteFileFromCollection: async (
    collectionName: string,
    fileName: string,
  ): Promise<{
    success: boolean;
    collection_name: string;
    file_name: string;
    chunks_deleted: number;
    message: string;
  }> => {
    const response = await fetch(
      `${API_BASE_URL}/vectors/collections/${encodeURIComponent(collectionName)}/files/${encodeURIComponent(fileName)}`,
      { method: "DELETE" },
    );
    if (!response.ok) throw new Error("Error deleting file from collection");
    return response.json();
  },

  // Agregar chunks a una colección
  addChunks: async (
    collectionName: string,
    chunks: Array<{ id: string; vector: number[]; payload: any }>,
  ): Promise<{
    success: boolean;
    collection_name: string;
    chunks_added: number;
    message: string;
  }> => {
    const response = await fetch(`${API_BASE_URL}/vectors/chunks/add`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        collection_name: collectionName,
        chunks: chunks,
      }),
    });
    if (!response.ok) throw new Error("Error adding chunks");
    return response.json();
  },

  // ============================================================================
  // Chunking Operations
  // ============================================================================

  // Obtener perfiles de chunking predefinidos
  getChunkingProfiles: async (): Promise<{
    profiles: Array<{
      id: string;
      name: string;
      description: string;
      max_tokens: number;
      target_tokens: number;
      chunk_size: number;
      chunk_overlap: number;
      use_llm: boolean;
    }>;
  }> => {
    const response = await fetch(`${API_BASE_URL}/chunking/profiles`);
    if (!response.ok) throw new Error("Error fetching chunking profiles");
    return response.json();
  },

  // Generar preview de chunks (hasta 3 chunks)
  generateChunkPreview: async (config: {
    file_name: string;
    tema: string;
    max_tokens?: number;
    target_tokens?: number;
    chunk_size?: number;
    chunk_overlap?: number;
    use_llm?: boolean;
    custom_instructions?: string;
  }): Promise<{
    success: boolean;
    file_name: string;
    tema: string;
    chunks: Array<{
      index: number;
      text: string;
      page: number;
      file_name: string;
      tokens: number;
    }>;
    message: string;
  }> => {
    const response = await fetch(`${API_BASE_URL}/chunking/preview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error generating preview");
    }
    return response.json();
  },

  // Procesar PDF completo
  processChunkingFull: async (config: {
    file_name: string;
    tema: string;
    collection_name: string;
    max_tokens?: number;
    target_tokens?: number;
    chunk_size?: number;
    chunk_overlap?: number;
    use_llm?: boolean;
    custom_instructions?: string;
  }): Promise<{
    success: boolean;
    collection_name: string;
    file_name: string;
    total_chunks: number;
    chunks_added: number;
    message: string;
  }> => {
    const response = await fetch(`${API_BASE_URL}/chunking/process`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error processing PDF");
    }
    return response.json();
  },

  // ============================================================================
  // Schemas API
  // ============================================================================

  // Crear schema
  createSchema: async (schema: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/schemas/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(schema),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || "Error creando schema");
    }
    return response.json();
  },

  // Listar schemas
  listSchemas: async (tema?: string): Promise<any[]> => {
    const url = tema
      ? `${API_BASE_URL}/schemas/?tema=${encodeURIComponent(tema)}`
      : `${API_BASE_URL}/schemas/`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Error listando schemas");
    return response.json();
  },

  // Obtener schema por ID
  getSchema: async (schema_id: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/schemas/${schema_id}`);
    if (!response.ok) throw new Error("Error obteniendo schema");
    return response.json();
  },

  // Actualizar schema
  updateSchema: async (schema_id: string, schema: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/schemas/${schema_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(schema),
    });
    if (!response.ok) throw new Error("Error actualizando schema");
    return response.json();
  },

  // Eliminar schema
  deleteSchema: async (schema_id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/schemas/${schema_id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Error eliminando schema");
  },

  // Validar schema
  validateSchema: async (schema: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/schemas/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(schema),
    });
    if (!response.ok) throw new Error("Error validando schema");
    return response.json();
  },

  // ============================================================================
  // LandingAI Processing
  // ============================================================================

  // Procesar con LandingAI
  processWithLandingAI: async (config: {
    file_name: string;
    tema: string;
    collection_name: string;
    mode: "quick" | "extract";
    schema_id?: string;
    include_chunk_types?: string[];
    max_tokens_per_chunk?: number;
    merge_small_chunks?: boolean;
  }): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/chunking-landingai/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Error procesando con LandingAI");
    }
    return response.json();
  },
};
