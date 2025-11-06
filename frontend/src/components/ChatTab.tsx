import { MessageCircle, Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ChatTabProps {
  selectedTema: string | null;
}

export function ChatTab({ selectedTema }: ChatTabProps) {
  if (!selectedTema) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <MessageCircle className="w-12 h-12 text-gray-400 mb-4" />
        <p className="text-gray-500">
          Selecciona un dataroom para iniciar el chat
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <MessageCircle className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Chat con {selectedTema}
            </h3>
            <p className="text-sm text-gray-600">
              Haz preguntas sobre los documentos de este dataroom
            </p>
          </div>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Welcome Message */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-blue-100 rounded-full">
              <Bot className="w-4 h-4 text-blue-600" />
            </div>
            <div className="flex-1 bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-800">
                ¡Hola! Soy tu asistente de IA para el dataroom <strong>{selectedTema}</strong>.
                Puedes hacerme preguntas sobre los documentos almacenados aquí.
              </p>
            </div>
          </div>

          {/* Placeholder for future messages */}
          <div className="text-center py-8">
            <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              Chat Inteligente
            </h4>
            <p className="text-gray-500 max-w-md mx-auto">
              El chat estará disponible próximamente. Podrás hacer preguntas sobre los
              documentos y obtener respuestas basadas en el contenido del dataroom.
            </p>
          </div>
        </div>
      </div>

      {/* Chat Input Area */}
      <div className="border-t border-gray-200 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <Input
                placeholder={`Pregunta algo sobre ${selectedTema}...`}
                disabled
                className="w-full"
              />
            </div>
            <Button disabled className="gap-2">
              <Send className="w-4 h-4" />
              Enviar
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Esta funcionalidad estará disponible próximamente
          </p>
        </div>
      </div>
    </div>
  );
}
