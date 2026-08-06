import { Bell, Search, User } from "lucide-react"

export function Header() {
  return (
    <header className="sticky top-0 z-10 flex h-16 flex-shrink-0 items-center justify-between border-b border-slate-200 bg-white/80 backdrop-blur-sm px-4 sm:px-6 lg:px-8">
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-400">Pages</span>
        <span className="text-slate-400">/</span>
        <span className="text-slate-800 font-medium">Dashboard Overview</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative hidden sm:block">
          <input
            id="search-field"
            className="bg-slate-100 border-none rounded-lg py-1.5 px-4 text-xs w-64 focus:ring-2 focus:ring-blue-500"
            placeholder="Search records..."
            type="search"
            name="search"
          />
        </div>
        <button type="button" className="p-2 text-slate-400 hover:text-slate-600 relative">
          <span className="sr-only">View notifications</span>
          <Bell className="h-5 w-5" aria-hidden="true" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        </button>
      </div>
    </header>
  )
}
