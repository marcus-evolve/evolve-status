import './Footer.css'

interface FooterProps {
  generatedAt?: string
}

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  })
}

function Footer({ generatedAt }: FooterProps) {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <a href="https://joinevolve.app" target="_blank" rel="noopener noreferrer" className="footer-link">
          Go to website
        </a>
        
        {generatedAt && (
          <div className="footer-updated">
            Last updated: {formatTime(generatedAt)}
          </div>
        )}
      </div>
    </footer>
  )
}

export default Footer
