import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="max-w-md mx-auto p-6 space-y-4">
        <h1 className="text-3xl font-bold text-center">
          ¡Shadcn UI ! 
        </h1>
        
        <div className="space-y-2">
          <Button className="w-full">
            Botón Principal
          </Button>
          
          <Button variant="secondary" className="w-full">
            Botón Secundario
          </Button>
          
          <Button variant="destructive" className="w-full">
            Botón de Eliminación
          </Button>
          
          <Button variant="outline" className="w-full">
            Botón con Borde
          </Button>
        </div>
      </div>
    </div>
  )
}

export default App