import { useState } from 'react';
import { ChevronDown, ChevronUp, ShieldCheck, ExternalLink } from 'lucide-react';
import { SourceCredibility } from '../../types/api';

interface SourceDetailsProps {
  credibility?: SourceCredibility;
}

export default function SourceDetails({ credibility }: SourceDetailsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!credibility) {
    return null;
  }

  const categoryLabels = {
    documented: 'Documented Provenance',
    partially_documented: 'Partially Documented',
    unknown: 'Unknown Provenance',
  };

  const categoryBadgeStyle = {
    documented: 'border-charcoal bg-charcoal text-ivory',
    partially_documented: 'border-charcoal text-charcoal bg-charcoal/10',
    unknown: 'border-charcoal/40 text-charcoal/70 border-dashed',
  };

  const provenance = credibility.provenance_category || 'unknown';

  return (
    <div className="mt-3 text-xs border border-charcoal/15 rounded-md p-3 bg-charcoal/[0.02]">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldCheck size={14} className="text-charcoal/70" />
          <span className="font-semibold text-charcoal">Source Provenance:</span>
          <span
            className={`px-2 py-0.5 text-[11px] font-medium rounded border ${
              categoryBadgeStyle[provenance] || categoryBadgeStyle.unknown
            }`}
          >
            {categoryLabels[provenance] || provenance}
          </span>
        </div>
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="text-charcoal/60 hover:text-charcoal flex items-center gap-1 focus-ring p-1 rounded"
          aria-expanded={expanded}
        >
          <span>{expanded ? 'Hide Signals' : 'View Signals'}</span>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-charcoal/10 space-y-2">
          <p className="text-[11px] text-charcoal/60 leading-normal">
            Signals evaluate available documentation for the source. Missing metadata (such as an individual
            author) is common and does not inherently denote an ungrounded source.
          </p>

          <div className="space-y-1.5 mt-2">
            {credibility.signals.map((sig, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between py-1 border-b border-charcoal/5 last:border-0 text-charcoal/80"
              >
                <div>
                  <span className="font-medium text-charcoal">{sig.name}:</span>{' '}
                  <span className={sig.status === 'unknown' ? 'italic text-charcoal/60' : ''}>
                    {sig.value}
                  </span>
                  {sig.reason && (
                    <div className="text-[10px] text-charcoal/60 mt-0.5">{sig.reason}</div>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {sig.supporting_url && (
                    <a
                      href={sig.supporting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-charcoal/60 hover:text-charcoal underline flex items-center gap-0.5"
                    >
                      Policy <ExternalLink size={10} />
                    </a>
                  )}
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded border ${
                      sig.status === 'observed'
                        ? 'border-charcoal/30 bg-charcoal/5 text-charcoal'
                        : 'border-dashed border-charcoal/30 text-charcoal/50'
                    }`}
                  >
                    {sig.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
