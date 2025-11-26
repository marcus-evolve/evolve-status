import { ReactNode } from 'react'
import './Header.css'

interface HeaderProps {
  children?: ReactNode
}

function Header({ children }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-inner">
        <a href="https://joinevolve.app" className="header-logo" target="_blank" rel="noopener noreferrer">
          <img src="./logo.png" alt="Evolve" className="logo-image" />
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
