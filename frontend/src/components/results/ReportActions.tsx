import Button from '../ui/Button';
import { Printer, RefreshCw } from 'lucide-react';
import { AnalysisResponse } from '../../types/api';
import { printReport } from '../../lib/export';

interface ReportActionsProps {
  data: AnalysisResponse;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export default function ReportActions({ onRefresh, isRefreshing }: ReportActionsProps) {
  return (
    <div className="flex items-center gap-2 no-print">
      <Button
        variant="ghost"
        onClick={onRefresh}
        disabled={isRefreshing}
        title="Refresh and re-verify analysis"
        aria-label="Refresh and re-verify analysis"
        className="flex items-center gap-1.5"
      >
        <RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />
        <span className="hidden sm:inline text-xs font-medium">Refresh</span>
      </Button>

      <Button
        variant="secondary"
        onClick={printReport}
        title="Print / Save PDF"
        aria-label="Print or save as PDF"
        className="flex items-center gap-2"
      >
        <Printer size={18} />
        <span className="hidden sm:inline">Print</span>
      </Button>
    </div>
  );
}
