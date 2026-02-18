import { Link, Outlet, useLocation } from 'react-router-dom'
import { FiHome, FiCheckSquare, FiBarChart2 } from 'react-icons/fi'

const navItems = [
  { to: '/', label: 'Toplantılar', icon: FiHome },
  { to: '/tasks', label: 'Görevler', icon: FiCheckSquare },
  { to: '/reports', label: 'Raporlar', icon: FiBarChart2 },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-indigo-600">
            Toplantı Asistanı
          </Link>
          <div className="flex gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === to
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon size={18} />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
