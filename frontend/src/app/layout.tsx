import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "InfluencerFlow - Campaign Management",
  description: "Create and manage influencer marketing campaigns",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
          <header className="sticky top-0 z-30 w-full border-b border-slate-200 bg-white/90 backdrop-blur-sm">
            <div className="container mx-auto px-4 py-3 flex items-center justify-between">
              <Link href="/" className="flex items-center space-x-2">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  className="h-7 w-7 text-indigo-600"
                >
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <span className="text-xl font-bold text-slate-900">InfluencerFlow</span>
              </Link>
              
              <nav className="hidden md:flex space-x-1">
                <Link href="/campaigns" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Campaigns
                </Link>
                <Link href="/creators" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Creators
                </Link>
                <Link href="/outreach" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Outreach
                </Link>
                <Link href="/negotiation" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Negotiation
                </Link>
                <Link href="/contract" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Contracts
                </Link>
                <Link href="/analytics" className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-100 transition-colors">
                  Analytics
                </Link>
              </nav>
              
              <div className="hidden md:flex items-center space-x-2">
                <button className="px-3 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
                  Sign In
                </button>
                <button className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-colors">
                  Get Started
                </button>
              </div>
              
              <button className="md:hidden p-2 rounded-md text-slate-700 hover:bg-slate-100 transition-colors">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  width="24" 
                  height="24" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  className="h-6 w-6"
                >
                  <line x1="4" x2="20" y1="12" y2="12"></line>
                  <line x1="4" x2="20" y1="6" y2="6"></line>
                  <line x1="4" x2="20" y1="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </header>
          
          <main className="pt-6">
            {children}
          </main>
          
          <footer className="bg-white border-t border-slate-200 py-6 mt-12">
            <div className="container mx-auto px-4">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div className="text-slate-500 text-sm mb-4 md:mb-0">
                  © {new Date().getFullYear()} InfluencerFlow. All rights reserved.
                </div>
                <div className="flex space-x-6">
                  <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
                    Privacy
                  </a>
                  <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
                    Terms
                  </a>
                  <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
                    Contact
                  </a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
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