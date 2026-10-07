import { useState } from 'react';
import { ClaimResult } from '../../types/api';
import SourceDetails from './SourceDetails';
import Badge from '../ui/Badge';
import { ExternalLink, ChevronDown, ChevronUp, Layers } from 'lucide-react';

interface EvidencePanelProps {
  claim: ClaimResult;
}

export default function EvidencePanel({ claim }: EvidencePanelProps) {
  const [expandedContext, setExpandedContext] = useState<Record<string, boolean>>({});

  const toggleContext = (id: string) => {
    setExpandedContext((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const stanceBadgeClass = {
    supports: 'border-charcoal bg-charcoal/10 text-charcoal',
    contradicts: 'border-charcoal bg-charcoal text-ivory',
    neutral: 'border-charcoal/30 border-dashed text-charcoal/70',
  };

  return (
    <div className="border border-charcoal/15 rounded-lg p-6 bg-ivory shadow-sm sticky top-6 space-y-6">
      {/* Selected Claim Overview */}
      <div className="border-b border-charcoal/10 pb-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <span className="text-xs uppercase tracking-wider font-semibold text-charcoal/60">
            Selected Proposition ({claim.id})
          </span>
          <Badge outcome={claim.outcome} />
        </div>

        <p className="font-serif text-lg font-bold text-charcoal leading-snug mb-3">
          "{claim.claim_text}"
        </p>

        {claim.reason && (
          <div className="p-3 bg-charcoal/5 rounded border border-charcoal/10 text-xs sm:text-sm text-charcoal/80 leading-relaxed">
            <span className="font-semibold text-charcoal">Decision Basis: </span>
            {claim.reason}
          </div>
        )}

        {/* Linguistic indicators */}
        {claim.linguistic_features && (
          <div className="mt-3 flex flex-wrap gap-1.5 text-[11px] text-charcoal/60">
            {claim.linguistic_features.has_negation && (
              <span className="px-2 py-0.5 border border-charcoal/20 rounded">Contains Negation</span>
            )}
            {claim.linguistic_features.has_qualifier && (
              <span className="px-2 py-0.5 border border-charcoal/20 rounded">Contains Qualifier</span>
            )}
            {claim.linguistic_features.has_attribution && (
              <span className="px-2 py-0.5 border border-charcoal/20 rounded">Reported Speech</span>
            )}
            {claim.linguistic_features.numbers && claim.linguistic_features.numbers.length > 0 && (
              <span className="px-2 py-0.5 border border-charcoal/20 rounded">
                Numeric Claims: {claim.linguistic_features.numbers.join(', ')}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Retrieved Evidence Items */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-serif text-base font-bold text-charcoal flex items-center gap-2">
            <Layers size={16} /> Supporting & Contradicting Evidence ({claim.evidence.length})
          </h3>
          <span className="text-xs text-charcoal/60">Ranked by relevance</span>
        </div>

        {claim.evidence.length === 0 ? (
          <div className="text-center py-8 border border-dashed border-charcoal/20 rounded-md text-sm text-charcoal/60">
            No specific evidence passages were retrieved for this claim statement.
          </div>
        ) : (
          <div className="space-y-6">
            {claim.evidence.map((ev, i) => {
              const stanceStyle =
                stanceBadgeClass[ev.stance] || stanceBadgeClass.neutral;
              const hasFull = Boolean(ev.full_context && ev.full_context !== ev.excerpt);
              const isFullExpanded = Boolean(expandedContext[ev.id || i]);

              return (
                <div
                  key={ev.id || i}
                  className="border border-charcoal/15 rounded-md p-4 bg-white/60 space-y-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      {ev.url ? (
                        <a
                          href={ev.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-sm text-charcoal hover:underline inline-flex items-center gap-1 focus-ring"
                        >
                          {ev.title || 'Referenced Document'}{' '}
                          <ExternalLink size={12} className="text-charcoal/50" />
                        </a>
                      ) : (
                        <span className="font-medium text-sm text-charcoal">
                          {ev.title || 'Referenced Document'}
                        </span>
                      )}
                      <div className="text-xs text-charcoal/60 mt-0.5">
                        {ev.publisher || 'Unknown Publisher'}
                        {ev.publication_date ? ` • ${ev.publication_date}` : ''}
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <span
                        className={`text-xs px-2.5 py-1 rounded font-medium tracking-wide uppercase border ${stanceStyle}`}
                      >
                        {ev.stance}
                      </span>
                      {ev.stance_scores && (
                        <div className="text-[10px] text-charcoal/50 mt-1 font-mono">
                          NLI: E {Math.round((ev.stance_scores.entailment || 0) * 100)}% | C{' '}
                          {Math.round((ev.stance_scores.contradiction || 0) * 100)}%
                        </div>
                      )}
                    </div>
                  </div>

                  <blockquote className="border-l-2 border-charcoal/30 pl-3 py-0.5 text-xs sm:text-sm text-charcoal/90 italic leading-relaxed">
                    "{ev.excerpt}"
                  </blockquote>

                  {hasFull && (
                    <div>
                      <button
                        type="button"
                        onClick={() => toggleContext(ev.id || String(i))}
                        className="text-[11px] text-charcoal/60 hover:text-charcoal flex items-center gap-1 underline focus-ring"
                      >
                        <span>{isFullExpanded ? 'Collapse context' : 'Expand full passage context'}</span>
                        {isFullExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </button>

                      {isFullExpanded && (
                        <div className="mt-2 p-2.5 bg-ivory rounded text-xs text-charcoal/80 leading-relaxed border border-charcoal/10 font-mono">
                          {ev.full_context}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Credibility signals */}
                  <SourceDetails credibility={ev.source_credibility} />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
