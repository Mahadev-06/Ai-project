import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../ui/Button';
import { useHistory } from '../../hooks/useHistory';
import { formatDateTime } from '../../utils/format';
import { Trash2, Search, FileText, ArrowRight } from 'lucide-react';

export default function HistoryPage() {
  const { history, loading, clear, remove } = useHistory();
  const [searchTerm, setSearchTerm] = useState('');
  const [modeFilter, setModeFilter] = useState<'all' | 'local' | 'live'>('all');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const navigate = useNavigate();

  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      const mode = item.report?.evidence_mode || 'local';
      if (modeFilter !== 'all' && mode !== modeFilter) return false;

      if (!searchTerm.trim()) return true;
      const term = searchTerm.toLowerCase();

      // Match ID
      if (item.id.toLowerCase().includes(term)) return true;

      // Match input summary
      if (item.report?.input_summary?.toLowerCase().includes(term)) return true;

      // Match claims
      const claims = item.report?.claims || [];
      return claims.some((c) => c.claim_text.toLowerCase().includes(term));
    });
  }, [history, searchTerm, modeFilter]);

  if (loading) {
    return (
      <div className="py-20 text-center text-sm text-charcoal/60">
        Loading saved reports from device storage...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end border-b border-charcoal/15 pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-charcoal tracking-tight">
            Saved Reports
          </h1>
          <p className="text-xs sm:text-sm text-charcoal/60 mt-1">
            Locally preserved analyses on your device ({history.length} total)
          </p>
        </div>

        {history.length > 0 && (
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={() => setShowClearConfirm(true)}
              className="text-xs"
            >
              Clear All Reports
            </Button>
          </div>
        )}
      </div>

      {/* Clear Confirmation Modal */}
      {showClearConfirm && (
        <div className="p-4 border border-charcoal bg-charcoal/5 rounded-md flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-xs font-medium text-charcoal">
            Are you sure you want to delete all locally saved reports? This action cannot be undone.
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={() => setShowClearConfirm(false)}
              className="text-xs"
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                clear();
                setShowClearConfirm(false);
              }}
              className="text-xs"
            >
              Confirm Clear
            </Button>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      {history.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search
              size={16}
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-charcoal/40"
            />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search reports by claim text, topic, or ID..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-ivory border border-charcoal/20 rounded-md focus-ring text-charcoal placeholder-charcoal/40"
            />
          </div>

          <div className="flex items-center gap-1 border border-charcoal/20 rounded-md p-1 bg-ivory text-xs">
            <button
              type="button"
              onClick={() => setModeFilter('all')}
              className={`px-3 py-1 rounded transition-colors ${
                modeFilter === 'all'
                  ? 'bg-charcoal text-ivory font-medium'
                  : 'text-charcoal/60 hover:text-charcoal'
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setModeFilter('local')}
              className={`px-3 py-1 rounded transition-colors ${
                modeFilter === 'local'
                  ? 'bg-charcoal text-ivory font-medium'
                  : 'text-charcoal/60 hover:text-charcoal'
              }`}
            >
              Local
            </button>
            <button
              type="button"
              onClick={() => setModeFilter('live')}
              className={`px-3 py-1 rounded transition-colors ${
                modeFilter === 'live'
                  ? 'bg-charcoal text-ivory font-medium'
                  : 'text-charcoal/60 hover:text-charcoal'
              }`}
            >
              Live
            </button>
          </div>
        </div>
      )}

      {/* List */}
      {history.length === 0 ? (
        <div className="text-center py-16 border border-charcoal/15 rounded-lg bg-ivory space-y-3">
          <FileText size={32} className="text-charcoal/30 mx-auto" />
          <p className="text-charcoal/80 text-sm font-medium">No saved reports found.</p>
          <p className="text-charcoal/50 text-xs max-w-sm mx-auto">
            When you run an analysis, completed reports are automatically archived in your browser for offline review.
          </p>
          <div className="pt-2">
            <Button onClick={() => navigate('/')}>Analyze a Claim</Button>
          </div>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-charcoal/20 rounded-lg text-sm text-charcoal/60">
          No reports match your current search criteria.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredHistory.map((item) => {
            const report = item.report;
            const claimsCount = report?.claims?.length || 0;
            const summary =
              report?.input_summary ||
              (report?.claims?.[0]?.claim_text
                ? `"${report.claims[0].claim_text}"`
                : `Analysis #${item.id.slice(0, 8)}`);

            return (
              <div
                key={item.id}
                onClick={() => navigate(`/results/${item.id}`)}
                className="bg-white border border-charcoal/15 rounded-lg p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center hover:border-charcoal/50 transition-all cursor-pointer group focus-ring gap-4"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    navigate(`/results/${item.id}`);
                  }
                }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[11px] font-mono font-semibold text-charcoal/60">
                      #{item.id.slice(0, 8)}
                    </span>
                    <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.2 border border-charcoal/20 rounded text-charcoal/70">
                      {report?.evidence_mode || 'Local'}
                    </span>
                    <span className="text-xs text-charcoal/40">•</span>
                    <span className="text-xs text-charcoal/60">
                      {formatDateTime(item.created_at)}
                    </span>
                  </div>

                  <p className="font-serif font-semibold text-sm sm:text-base text-charcoal truncate">
                    {summary}
                  </p>

                  <div className="flex items-center gap-3 text-xs text-charcoal/60 mt-1">
                    <span>{claimsCount} claim proposition(s)</span>
                    {report?.corpus_version && <span>Corpus v{report.corpus_version}</span>}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      remove(item.id);
                    }}
                    className="p-2 text-charcoal/40 hover:text-charcoal hover:bg-charcoal/5 focus-ring rounded transition-colors"
                    aria-label={`Delete report ${item.id.slice(0, 8)}`}
                    title="Delete report"
                  >
                    <Trash2 size={16} />
                  </button>

                  <span className="text-xs text-charcoal/70 group-hover:text-charcoal inline-flex items-center gap-1 font-medium pl-1">
                    Open <ArrowRight size={14} />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
