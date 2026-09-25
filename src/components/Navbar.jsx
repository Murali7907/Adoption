import React, { useState, useEffect } from 'react'
import { Cloudmark, MenuIcon } from './icons'
import './Navbar.css'

const LINKS = ['Home', 'Products', 'Our business', 'Clients', 'About']

export function Navbar() {
  const [active, setActive] = useState('Home')
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  const closeMenu = () => setOpen(false)

  return (
    <header className="nav">
      <div className="nav__inner shell">
        <a className="nav__brand" href="#top">
          <Cloudmark />
          <span>Glowinn</span>
        </a>

        <nav className="nav__rail" aria-label="Primary">
          {LINKS.map((label) => {
            const href = `#${label.toLowerCase().replace(/\s+/g, '-')}`
            return (
              <a
                key={label}
                href={href}
                className={active === label ? 'is-active' : ''}
                onClick={() => setActive(label)}
              >
                {label}
              </a>
            )
          })}
        </nav>

        <div className="nav__actions">
          <a className="nav__register" href="#register">
            Register
          </a>
          <a className="btn btn--ink" href="#buy">
            Buy Now
          </a>
        </div>

        <button
          className="nav__toggle"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-label={open ? 'Close menu' : 'Open menu'}
        >
          <MenuIcon open={open} />
        </button>
      </div>

      {open && (
        <div className="nav__sheet">
          {LINKS.map((label) => (
            <a
              key={label}
              href={`#${label.toLowerCase().replace(/\s+/g, '-')}`}
              onClick={() => {
                setActive(label)
                closeMenu()
              }}
            >
              {label}
            </a>
          ))}
          <a href="#register" onClick={closeMenu}>
            Register
          </a>
          <a className="btn btn--pearl" href="#buy" onClick={closeMenu}>
            Buy Now
          </a>
        </div>
      )}
    </header>
  )
}
