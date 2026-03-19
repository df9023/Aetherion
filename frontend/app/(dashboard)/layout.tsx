import { Sidebar } from "@/components/sidebar"
import { TopBar } from "@/components/top-bar"
import { Providers } from "@/components/providers"
import { Toaster } from "@/components/ui/sonner"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <div className="min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-64 min-h-screen">
          <TopBar />
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </div>
      <Toaster />
    </Providers>
  )
}
