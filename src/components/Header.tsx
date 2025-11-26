import { ReactNode } from 'react'
import './Header.css'

interface HeaderProps {
  children?: ReactNode
}

function Header({ children }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-inner">
        <a href="/" className="header-logo">
          <svg className="logo-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="evolve-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22c55e" />
                <stop offset="50%" stopColor="#14b8a6" />
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
            </defs>
            <path
              d="M16 2L4 8v8c0 7.18 5.12 13.88 12 16 6.88-2.12 12-8.82 12-16V8L16 2z"
              stroke="url(#evolve-grad)"
              strokeWidth="2"
              fill="none"
            />
            <path
              d="M10 16l4 4 8-8"
              stroke="url(#evolve-grad)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
            />
          </svg>
          <span className="logo-text">Evolve</span>
          <span className="logo-status">Status</span>
        </a>
        
        <nav className="header-nav">
          {children}
          <a href="./feed.xml" className="header-link" title="RSS Feed">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 11a9 9 0 0 1 9 9" />
              <path d="M4 4a16 16 0 0 1 16 16" />
              <circle cx="5" cy="19" r="1" fill="currentColor" />
            </svg>
            <span className="sr-only">RSS Feed</span>
          </a>
        </nav>
      </div>
    </header>
  )
}

export default Header
