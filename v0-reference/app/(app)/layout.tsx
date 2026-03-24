import { Sidebar } from '@/components/sidebar'
import { Topbar } from '@/components/topbar'

export default function AppShellLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />
      <div className="ml-64 flex min-h-screen flex-col">
        {children}
      </div>
    </div>
  )
}
