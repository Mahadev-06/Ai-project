import Button from '../ui/Button';
import { Download, Printer, Save, RefreshCw } from 'lucide-react';
import { AnalysisResponse } from '../../types/api';
import { exportToJson, printReport } from '../../lib/export';
import { saveHistory } from '../../lib/db';
import { useNavigate } from 'react-router-dom';

interface ReportActionsProps {
  data: AnalysisResponse;
}

export default function ReportActions({ data }: ReportActionsProps) {
  const navigate = useNavigate();

  const handleSave = async () => {
    await saveHistory(data);
    alert('Report saved to history');
  };

  return (
    <div className="flex flex-wrap gap-2 no-print">
      <Button variant="ghost" onClick={() => navigate('/')} title="Analyze Another">
        <RefreshCw size={18} />
      </Button>
      <Button variant="ghost" onClick={handleSave} title="Save to Device">
        <Save size={18} />
      </Button>
      <Button variant="ghost" onClick={() => exportToJson(data, `report-${data.id}`)} title="Export JSON">
        <Download size={18} />
      </Button>
      <Button variant="secondary" onClick={printReport} title="Print / Save PDF" className="flex items-center gap-2">
        <Printer size={18} /> <span className="hidden sm:inline">Print</span>
      </Button>
    </div>
  );
}
