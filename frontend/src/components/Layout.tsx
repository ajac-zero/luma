import { useState } from 'react'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Menu } from 'lucide-react'
import { Sidebar } from './Sidebar'
import { Dashboard } from './Dashboard'
import { SchemaManagement } from '@/pages/SchemaManagement'
import { cn } from '@/lib/utils'

type View = 'dashboard' | 'schemas'

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [currentView, setCurrentView] = useState<View>('dashboard')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleNavigateToSchemas = () => {
    if (isProcessing) {
      alert('No puedes navegar mientras se está procesando un archivo. Por favor espera a que termine.')
      return
    }
    setCurrentView('schemas')
    setSidebarOpen(false)
  }

  const handleNavigateToDashboard = () => {
    if (isProcessing) {
      alert('No puedes navegar mientras se está procesando un archivo. Por favor espera a que termine.')
      return
    }
    setCurrentView('dashboard')
  }

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Desktop Sidebar */}
      <div
        className={cn(
          'hidden md:flex md:flex-col transition-all duration-300',
          isSidebarCollapsed ? 'md:w-20' : 'md:w-64'
        )}
      >
        <Sidebar
          onNavigateToSchemas={handleNavigateToSchemas}
          disabled={isProcessing}
          collapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
        />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden fixed top-4 left-4 z-40"
            disabled={isProcessing}
          >
            <Menu className="h-6 w-6" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <Sidebar
            onNavigateToSchemas={handleNavigateToSchemas}
            disabled={isProcessing}
          />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {currentView === 'dashboard' ? (
          <Dashboard onProcessingChange={setIsProcessing} />
        ) : (
          <div className="flex-1 overflow-auto">
            <SchemaManagement />
            <div className="fixed bottom-6 right-6">
              <Button onClick={handleNavigateToDashboard} disabled={isProcessing}>
                {isProcessing ? 'Procesando...' : 'Volver al Dashboard'}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
