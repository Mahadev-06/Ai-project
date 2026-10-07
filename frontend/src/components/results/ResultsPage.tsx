import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ClaimCard from './ClaimCard';
import EvidencePanel from './EvidencePanel';
import ReportActions from './ReportActions';
import ProgressView from '../progress/ProgressView';
import Button from '../ui/Button';
import { useAnalysis } from '../../hooks/useAnalysis';
import { getReportById } from '../../lib/db';
import { AlertTriangle, ArrowLeft, ShieldAlert } from 'lucide-react';
import { formatDateTime } from '../../utils/format';

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { analysis, loading, error, cancel, loadExisting, setAnalysis } = useAnalysis();
  const [selectedClaimId, setSelectedClaimId] = useState<string>('');

  // Load analysis on mount
  useEffect(() => {
    if (!id) return;

    // Check IndexedDB first for fast offline loading
    getReportById(id)
      .then((saved) => {
        if (saved && saved.report) {
          setAnalysis(saved);
        } else {
          loadExisting(id);
        }
      })
      .catch(() => {
        loadExisting(id);
      });
  }, [id, loadExisting, setAnalysis]);

  const report = analysis?.report;
  const claims = report?.claims || [];

  // Update selected claim if not set or out of bounds
  useEffect(() => {
    if (claims.length > 0 && (!selectedClaimId || !claims.find((c) => c.id === selectedClaimId))) {
      setSelectedClaimId(claims[0].id);
    }
  }, [claims, selectedClaimId]);

  const selectedClaim = claims.find((c) => c.id === selectedClaimId);

  // Status: Queued or Running
  if (
    (loading && !report) ||
    analysis?.status === 'queued' ||
    analysis?.status === 'running'
  ) {
    return (
      <div className="py-12">
        <ProgressView
          stage={analysis?.stage || 'validating'}
          onCancel={() => id && cancel(id)}
        />
      </div>
    );
  }

  // Status: Cancelled
  if (analysis?.status === 'cancelled') {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <div className="w-12 h-12 rounded-full border border-charcoal/30 flex items-center justify-center mx-auto text-charcoal">
          ✕
        </div>
        <h2 className="font-serif text-2xl font-bold text-charcoal">Analysis Cancelled</h2>
        <p className="text-sm text-charcoal/70">
          The verification task was halted before completion.
        </p>
        <div className="pt-4">
          <Button onClick={() => navigate('/')}>Start New Analysis</Button>
        </div>
      </div>
    );
  }

  // Status: Failed or Error
  if (analysis?.status === 'failed' || (error && !report)) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <ShieldAlert size={36} className="text-charcoal mx-auto" />
        <h2 className="font-serif text-2xl font-bold text-charcoal">Analysis Failed</h2>
        <p className="text-sm text-charcoal/70">
          {error || 'The system could not complete evidence processing for this input.'}
        </p>
        <div className="pt-4 flex justify-center gap-3">
          <Button variant="secondary" onClick={() => id && loadExisting(id)}>
            Retry Loading
          </Button>
          <Button onClick={() => navigate('/')}>Analyze Different Text</Button>
        </div>
      </div>
    );
  }

  // Completed or Partial with Report
  return (
    <div className="flex flex-col space-y-8 py-6">
      {/* Back button and navigation */}
      <div className="no-print">
        <button
          type="button"
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-charcoal/60 hover:text-charcoal transition-colors focus-ring p-1 rounded"
        >
          <ArrowLeft size={14} /> Back to Analysis Input
        </button>
      </div>

      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end border-b border-charcoal/15 pb-6 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase tracking-widest font-bold text-charcoal/60">
              ClaimLens Report
            </span>
            <span className="text-xs text-charcoal/40">•</span>
            <span className="text-xs font-mono text-charcoal/60">ID: {id?.slice(0, 8)}</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal tracking-tight">
            Evidence Verification Findings
          </h1>

          <div className="flex flex-wrap items-center gap-2 text-xs text-charcoal/70 mt-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-charcoal/5 border border-charcoal/10 font-medium text-charcoal">
              <span className="w-1.5 h-1.5 rounded-full bg-charcoal/60"></span>
              Hybrid RAG Pipeline
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-charcoal/5 border border-charcoal/10 text-charcoal/70">
              Verified {report?.analysis_date ? formatDateTime(report.analysis_date) : 'Recently'}
            </span>
          </div>
        </div>

        {analysis && (
          <div className="shrink-0">
            <ReportActions data={analysis} />
          </div>
        )}
      </div>

      {/* Coverage / System Warnings */}
      {report?.coverage_warnings && report.coverage_warnings.length > 0 && (
        <div className="p-4 border border-charcoal/20 bg-charcoal/5 rounded-md text-xs text-charcoal/80 space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-charcoal">
            <AlertTriangle size={14} /> System Notices:
          </div>
          <ul className="list-disc pl-5 space-y-0.5">
            {report.coverage_warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Main Results Grid */}
      {claims.length === 0 ? (
        <div className="text-center py-16 border border-charcoal/15 rounded-lg bg-ivory">
          <p className="text-charcoal/70 text-base font-medium">
            No checkable factual claims could be extracted from the submitted input.
          </p>
          <p className="text-charcoal/50 text-xs mt-2">
            The input may contain only questions, opinions, or greetings without empirical propositions.
          </p>
          <div className="mt-6">
            <Button onClick={() => navigate('/')}>Try another claim</Button>
          </div>
        </div>
      ) : claims.length === 1 ? (
        /* Unified Presentation for Single Claim (Removes redundant duplicate columns) */
        <div className="max-w-4xl mx-auto w-full">
          {selectedClaim && <EvidencePanel claim={selectedClaim} />}
        </div>
      ) : (
        /* Multi-Claim Master-Detail Grid */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Claims Column */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-charcoal/10">
              <h2 className="font-serif text-lg font-bold text-charcoal">
                Extracted Claims ({claims.length})
              </h2>
              <span className="text-xs text-charcoal/50">Select to inspect evidence</span>
            </div>

            <div className="space-y-3">
              {claims.map((claim) => (
                <ClaimCard
                  key={claim.id}
                  claim={claim}
                  isSelected={claim.id === selectedClaimId}
                  onClick={() => setSelectedClaimId(claim.id)}
                />
              ))}
            </div>
          </div>

          {/* Evidence Inspector Column */}
          <div className="lg:col-span-7">
            {selectedClaim ? (
              <EvidencePanel claim={selectedClaim} />
            ) : (
              <div className="p-8 border border-dashed border-charcoal/20 rounded-lg text-center text-sm text-charcoal/60">
                Select a claim on the left to review cited evidence and confidence scores.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
