import { Message, MessageContent } from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputActionAddAttachments,
  PromptInputActionMenu,
  PromptInputActionMenuContent,
  PromptInputActionMenuTrigger,
  PromptInputAttachment,
  PromptInputAttachments,
  PromptInputBody,
  PromptInputHeader,
  type PromptInputMessage,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputFooter,
  PromptInputTools,
} from "@/components/ai-elements/prompt-input";
import { Action, Actions } from "@/components/ai-elements/actions";
import { Fragment, useState, useEffect } from "react";
import { useChat } from "@ai-sdk/react";
import { Response } from "@/components/ai-elements/response";
import {
  CopyIcon,
  RefreshCcwIcon,
  MessageCircle,
  Bot,
  AlertCircle,
  PaperclipIcon,
  User,
} from "lucide-react";
import { AuditReport } from "./AuditReport";
import { WebSearchResults } from "./WebSearchResults";
import { Loader } from "@/components/ai-elements/loader";
import { DefaultChatTransport } from "ai";

interface ChatTabProps {
  selectedTema: string | null;
}

export function ChatTab({ selectedTema }: ChatTabProps) {
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const {
    messages,
    sendMessage,
    status,
    regenerate,
    error: chatError,
  } = useChat({
    transport: new DefaultChatTransport({
      api: "/api/v1/agent/chat",
      headers: {
        tema: selectedTema || "",
      },
    }),
    onError: (error) => {
      setError(`Error en el chat: ${error.message}`);
    },
  });

  // Clear error when starting new conversation
  useEffect(() => {
    if (status === "streaming") {
      setError(null);
    }
  }, [status]);

  const handleSubmit = (message: PromptInputMessage) => {
    const hasText = Boolean(message.text?.trim());
    const hasAttachments = Boolean(message.files?.length);

    if (!(hasText || hasAttachments)) {
      return;
    }

    setError(null);
    sendMessage(
      {
        text: message.text || "Enviado con archivos adjuntos",
        files: message.files,
      },
      {
        body: {
          dataroom: selectedTema,
          context: `Usuario está consultando sobre el dataroom: ${selectedTema}`,
        },
      },
    );
    setInput("");
  };

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
    <div className="flex flex-col h-[638px] max-h-[638px]">
      {/* Chat Content */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        <div className="max-w-4xl mx-auto w-full space-y-6 p-6">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="flex items-start gap-3 mb-6">
              <div className="p-2 bg-blue-100 rounded-full">
                <Bot className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1 bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-800">
                  ¡Hola! Soy tu asistente de IA para el dataroom{" "}
                  <strong>{selectedTema}</strong>. Puedes hacerme preguntas
                  sobre los documentos almacenados aquí.
                </p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertCircle className="w-4 h-4 text-red-600" />
              </div>
              <div className="flex-1 bg-red-50 rounded-lg p-4 border border-red-200">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}

          {/* Chat Messages */}
          {messages.map((message) => (
            <div key={message.id}>
              {message.parts.map((part, i) => {
                switch (part.type) {
                  case "text":
                    return (
                      <Fragment key={`${message.id}-${i}`}>
                        {message.role === "user" ? (
                          <div className="flex items-start gap-3 justify-end">
                            <div className="flex-1">
                              <Message
                                from={message.role}
                                className="max-w-none"
                              >
                                <MessageContent>
                                  <Response>{part.text}</Response>
                                </MessageContent>
                              </Message>
                            </div>
                            <div className="p-2 rounded-full flex-shrink-0 mt-1 bg-gray-100">
                              <User className="w-4 h-4 text-gray-600" />
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-start gap-3">
                            <div className="p-2 rounded-full flex-shrink-0 mt-1 bg-blue-100">
                              <Bot className="w-4 h-4 text-blue-600" />
                            </div>
                            <div className="flex-1">
                              <Message
                                from={message.role}
                                className="max-w-none"
                              >
                                <MessageContent>
                                  <Response>{part.text}</Response>
                                </MessageContent>
                              </Message>
                            </div>
                          </div>
                        )}
                        {message.role === "assistant" &&
                          i === message.parts.length - 1 && (
                            <div className="ml-12">
                              <Actions className="mt-2">
                                <Action
                                  onClick={() => regenerate()}
                                  label="Regenerar"
                                  disabled={status === "streaming"}
                                >
                                  <RefreshCcwIcon className="size-3" />
                                </Action>
                                <Action
                                  onClick={() =>
                                    navigator.clipboard.writeText(part.text)
                                  }
                                  label="Copiar"
                                >
                                  <CopyIcon className="size-3" />
                                </Action>
                              </Actions>
                            </div>
                          )}
                      </Fragment>
                    );
                  case "tool-build_audit_report":
                    switch (part.state) {
                      case "input-available":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="flex items-center gap-2 p-4 bg-blue-50 rounded-lg border border-blue-200"
                          >
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            <span className="text-sm text-blue-700">
                              Generando reporte de auditoría...
                            </span>
                          </div>
                        );
                      case "output-available":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="mt-4 w-full"
                          >
                            <div className="max-w-full overflow-hidden">
                              <AuditReport data={part.output} />
                            </div>
                          </div>
                        );
                      case "output-error":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="p-4 bg-red-50 border border-red-200 rounded-lg"
                          >
                            <div className="flex items-center gap-2">
                              <AlertCircle className="w-4 h-4 text-red-600" />
                              <span className="text-sm font-medium text-red-800">
                                Error generando reporte de auditoría
                              </span>
                            </div>
                            <p className="text-sm text-red-600 mt-1">
                              {part.errorText}
                            </p>
                          </div>
                        );
                      default:
                        return null;
                    }
                  case "tool-search_web_information":
                    switch (part.state) {
                      case "input-available":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="flex items-center gap-2 p-4 bg-green-50 rounded-lg border border-green-200"
                          >
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
                            <span className="text-sm text-green-700">
                              Searching the web...
                            </span>
                          </div>
                        );
                      case "output-available":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="mt-4 w-full"
                          >
                            <div className="max-w-full overflow-hidden">
                              <WebSearchResults data={part.output} />
                            </div>
                          </div>
                        );
                      case "output-error":
                        return (
                          <div
                            key={`${message.id}-${i}`}
                            className="p-4 bg-red-50 border border-red-200 rounded-lg"
                          >
                            <div className="flex items-center gap-2">
                              <AlertCircle className="w-4 h-4 text-red-600" />
                              <span className="text-sm font-medium text-red-800">
                                Error searching the web
                              </span>
                            </div>
                            <p className="text-sm text-red-600 mt-1">
                              {part.errorText}
                            </p>
                          </div>
                        );
                      default:
                        return null;
                    }
                  default:
                    return null;
                }
              })}
            </div>
          ))}
          {status === "streaming" && <Loader />}
          {status === "loading" && <Loader />}
        </div>
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 p-3 bg-gray-50/50 flex-shrink-0">
        <PromptInput
          onSubmit={handleSubmit}
          className="max-w-4xl mx-auto border-2 border-gray-200 rounded-xl focus-within:border-slate-500 transition-colors duration-200 bg-white"
          globalDrop
          multiple
        >
          <PromptInputHeader className="p-2 pb-0">
            <PromptInputAttachments>
              {(attachment) => <PromptInputAttachment data={attachment} />}
            </PromptInputAttachments>
          </PromptInputHeader>
          <PromptInputBody>
            <PromptInputTextarea
              onChange={(e) => setInput(e.target.value)}
              value={input}
              placeholder={`Pregunta algo sobre ${selectedTema}...`}
              disabled={status === "streaming" || status === "loading"}
              className="min-h-[60px] resize-none border-0 focus:ring-0 transition-all duration-200 text-base px-4 py-3 bg-white rounded-xl"
            />
          </PromptInputBody>
          <PromptInputFooter className="mt-3 flex justify-between items-center">
            <PromptInputTools>
              <PromptInputActionMenu>
                <PromptInputActionMenuTrigger>
                  <PaperclipIcon className="size-4" />
                </PromptInputActionMenuTrigger>
                <PromptInputActionMenuContent>
                  <PromptInputActionAddAttachments />
                </PromptInputActionMenuContent>
              </PromptInputActionMenu>
            </PromptInputTools>
            <PromptInputSubmit
              disabled={
                (!input.trim() && !status) ||
                status === "streaming" ||
                status === "loading"
              }
              status={status}
              className={`rounded-full px-6 py-2 font-medium transition-all duration-200 flex items-center gap-2 ${
                (!input.trim() && !status) ||
                status === "streaming" ||
                status === "loading"
                  ? "bg-gray-300 cursor-not-allowed text-gray-500"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            />
          </PromptInputFooter>
        </PromptInput>
      </div>
    </div>
  );
}
