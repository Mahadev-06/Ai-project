import { CheckCircle2, XCircle, AlertTriangle, HelpCircle, MinusCircle } from 'lucide-react';
import { ClaimOutcome } from '../../types/api';
import { getOutcomeDisplay } from '../../utils/format';

interface BadgeProps {
  outcome: ClaimOutcome;
}

export default function Badge({ outcome }: BadgeProps) {
  const display = getOutcomeDisplay(outcome);
  let styles = '';
  let Icon = MinusCircle;

  switch (outcome) {
    case 'supported':
      styles = 'border-charcoal border text-charcoal';
      Icon = CheckCircle2;
      break;
    case 'contradicted':
      styles = 'bg-charcoal text-ivory';
      Icon = XCircle;
      break;
    case 'conflicting':
      styles = 'border-charcoal border-dashed border text-charcoal';
      Icon = AlertTriangle;
      break;
    case 'insufficient':
      styles = 'border-charcoal border-dotted border-2 text-charcoal';
      Icon = HelpCircle;
      break;
    case 'not_checkable':
      styles = 'bg-charcoal/10 text-charcoal';
      Icon = MinusCircle;
      break;
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles}`}>
      <Icon className="w-4 h-4 mr-1.5" />
      {display}
    </span>
  );
}
