import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isAfterAnalyze = location.pathname.startsWith('/results');

  // "After analyze header buttons shouldn't be there"
  // When viewing results after analysis, hide header buttons completely.
  // Also, remove "Saved Reports" and "Methodology" from navigation.
  const navLinks = isAfterAnalyze
    ? []
    : [{ to: '/', label: 'Analyze' }];

  return (
    <header className="border-b border-charcoal/15 bg-ivory sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Wordmark */}
          <div className="flex-shrink-0 flex items-center">
            <Link
              to="/"
              className="font-serif text-2xl font-bold text-charcoal tracking-tight focus-ring p-1 rounded"
              onClick={() => setMobileMenuOpen(false)}
            >
              ClaimLens
            </Link>
          </div>

          {/* Desktop Nav */}
          {navLinks.length > 0 && (
            <nav className="hidden sm:flex space-x-6 text-sm">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`py-2 px-3 rounded font-medium transition-colors focus-ring ${
                      isActive
                        ? 'bg-charcoal text-ivory'
                        : 'text-charcoal/70 hover:text-charcoal hover:bg-charcoal/5'
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          )}

          {/* Mobile Menu Toggle */}
          {navLinks.length > 0 && (
            <div className="sm:hidden flex items-center">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="min-w-[44px] min-h-[44px] flex items-center justify-center text-charcoal focus-ring rounded"
                aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && navLinks.length > 0 && (
        <div className="sm:hidden border-t border-charcoal/10 bg-ivory px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`block py-3 px-3 rounded text-base font-medium min-h-[44px] flex items-center ${
                  isActive
                    ? 'bg-charcoal text-ivory'
                    : 'text-charcoal/80 hover:bg-charcoal/5'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
