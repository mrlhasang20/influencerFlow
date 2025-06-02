// app/layout.tsx
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/Sidebar'
import TopNav from '@/components/TopNav'
import { Providers } from './providers'
import { ErrorBoundary } from '@/components/ErrorBoundary'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ErrorBoundary>
            <div className="flex h-screen">
              <Sidebar />
              <div className="flex-1 flex flex-col">
                <TopNav />
                <main className="flex-1 p-6 bg-gray-50 overflow-auto">
            {children}
          </main>
        </div>
            </div>
          </ErrorBoundary>
        </Providers>
      </body>
    </html>
  )
}