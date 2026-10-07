import Badge from '../ui/Badge';
import { ClaimResult } from '../../types/api';

interface ClaimCardProps {
  claim: ClaimResult;
  isSelected: boolean;
  onClick: () => void;
}

export default function ClaimCard({ claim, isSelected, onClick }: ClaimCardProps) {
  return (
    <div
      onClick={onClick}
      className={`p-5 rounded-lg border transition-all cursor-pointer focus-ring text-left ${
        isSelected
          ? 'border-charcoal bg-charcoal/5 shadow-xs'
          : 'border-charcoal/15 bg-white hover:border-charcoal/40 hover:bg-charcoal/[0.02]'
      }`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-pressed={isSelected}
    >
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-2.5">
        <p className="font-serif text-base font-bold text-charcoal leading-snug">
          "{claim.claim_text}"
        </p>
        <div className="shrink-0">
          <Badge outcome={claim.outcome} />
        </div>
      </div>

      {claim.reason && (
        <p className="text-xs text-charcoal/70 line-clamp-2 leading-relaxed">
          {claim.reason}
        </p>
      )}

      <div className="mt-3 pt-2 border-t border-charcoal/5 flex items-center justify-between text-[11px] text-charcoal/50">
        <span>Evidence: {claim.evidence?.length || 0} cited item(s)</span>
        <span className="font-medium text-charcoal/80">
          {isSelected ? 'Viewing details →' : 'Click to inspect'}
        </span>
      </div>
    </div>
  );
}
