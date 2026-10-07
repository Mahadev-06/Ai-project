import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-charcoal/15 bg-ivory py-8 mt-16 no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center text-xs text-charcoal/60 gap-4">
        <div>
          <p className="font-serif font-semibold text-charcoal text-sm">
            ClaimLens — University AI Capstone Project
          </p>
          <p className="text-[11px] text-charcoal/50 mt-0.5">
            AI-Based Misinformation Detection System Using NLP, Information Retrieval and Source Credibility Analysis
          </p>
        </div>

        <div className="flex items-center gap-6 text-xs font-medium">
          <Link to="/methodology" className="hover:text-charcoal transition-colors focus-ring">
            Methodology & Models
          </Link>
          <Link to="/history" className="hover:text-charcoal transition-colors focus-ring">
            Saved Reports
          </Link>
          <Link to="/" className="hover:text-charcoal transition-colors focus-ring">
            Analyze
          </Link>
        </div>
      </div>
    </footer>
  );
}
