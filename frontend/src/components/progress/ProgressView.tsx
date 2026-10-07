import { useState, useEffect } from 'react';
import { Check } from 'lucide-react';
import Button from '../ui/Button';
import Spinner from '../ui/Spinner';

interface ProgressViewProps {
  stage?: string;
  onCancel: () => void;
}

interface StageConfig {
  id: string;
  label: string;
  desc: string;
  progress: number;
}

const STAGES: StageConfig[] = [
  {
    id: 'validating',
    label: 'Validating Input',
    desc: 'Checking language, text boundaries, and input integrity',
    progress: 18,
  },
  {
    id: 'extracting',
    label: 'Extracting Claims',
    desc: 'Identifying checkable factual statements via NLP models',
    progress: 38,
  },
  {
    id: 'retrieving',
    label: 'Retrieving Evidence',
    desc: 'Searching offline factual corpus and live web resources',
    progress: 62,
  },
  {
    id: 'comparing',
    label: 'Evaluating Stance',
    desc: 'Cross-encoder natural language inference (support / contradiction)',
    progress: 85,
  },
  {
    id: 'preparing',
    label: 'Compiling Report',
    desc: 'Applying decision policy and formatting source citations',
    progress: 96,
  },
];

export default function ProgressView({ stage = 'validating', onCancel }: ProgressViewProps) {
  // Target index determined by current backend stage
  const targetIndex = Math.max(
    0,
    STAGES.findIndex((s) => s.id === stage)
  );

  // visualIndex smoothly eases forward so transitions are fluid and observable
  const [visualIndex, setVisualIndex] = useState(targetIndex);

  useEffect(() => {
    if (visualIndex < targetIndex) {
      const timer = window.setTimeout(() => {
        setVisualIndex((prev) => Math.min(prev + 1, targetIndex));
      }, 280);
      return () => clearTimeout(timer);
    } else if (visualIndex > targetIndex) {
      // Direct reset if stage rewinds (e.g. restart)
      setVisualIndex(targetIndex);
    }
  }, [visualIndex, targetIndex]);

  const currentStage = STAGES[visualIndex] || STAGES[0];
  const progressPercent = currentStage.progress;

  return (
    <div className="max-w-xl mx-auto w-full p-6 sm:p-8 border border-charcoal/15 rounded-lg bg-ivory shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col items-center justify-center text-center space-y-3">
        <Spinner size={36} />
        <div>
          <h2 className="font-serif text-2xl font-bold text-charcoal">Analyzing Evidence</h2>
          <p className="text-sm text-charcoal/70 mt-1 max-w-md mx-auto">
            Verifying factual statements using hybrid retrieval, live web verification, and natural language inference.
          </p>
        </div>
      </div>

      {/* Progress Bar & Status */}
      <div className="pt-2 pb-1 space-y-2 border-t border-charcoal/10">
        <div className="flex items-center justify-between text-xs text-charcoal/80 font-medium">
          <span>
            Step {visualIndex + 1} of {STAGES.length}:{' '}
            <strong className="text-charcoal">{currentStage.label}</strong>
          </span>
          <span className="font-mono text-charcoal font-semibold">{progressPercent}%</span>
        </div>
        <div className="h-2 w-full bg-charcoal/10 rounded-full overflow-hidden p-[1px]">
          <div
            className="h-full bg-charcoal rounded-full transition-all duration-500 ease-out relative overflow-hidden"
            style={{ width: `${progressPercent}%` }}
          >
            {/* Subtle animated light shimmer to signal active processing */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-ivory/20 to-transparent animate-shimmer" />
          </div>
        </div>
      </div>

      {/* Vertical Stepper with connecting line and active animations */}
      <div className="space-y-1 text-left pt-2 border-t border-charcoal/10">
        {STAGES.map((s, idx) => {
          const isDone = idx < visualIndex;
          const isCurrent = idx === visualIndex;

          return (
            <div key={s.id} className="relative flex items-start gap-3.5">
              {/* Stepper Indicator + Vertical Connecting Line */}
              <div className="flex flex-col items-center shrink-0">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 transition-all duration-300 relative ${
                    isDone
                      ? 'bg-charcoal text-ivory border border-charcoal shadow-sm'
                      : isCurrent
                      ? 'bg-ivory text-charcoal border-2 border-charcoal/20 shadow-sm'
                      : 'border border-charcoal/25 text-charcoal/40 bg-ivory'
                  }`}
                  aria-label={`${s.label}: ${isDone ? 'Completed' : isCurrent ? 'In Progress' : 'Pending'}`}
                >
                  {isDone ? (
                    <Check size={14} className="stroke-[3] text-ivory" />
                  ) : isCurrent ? (
                    <>
                      {/* Active continuous spinning ring around the current step number */}
                      <div className="absolute -inset-[2px] rounded-full border-2 border-transparent border-t-charcoal border-r-charcoal animate-spin" />
                      <span className="text-xs font-bold text-charcoal">{idx + 1}</span>
                    </>
                  ) : (
                    <span>{idx + 1}</span>
                  )}
                </div>

                {/* Connecting Line to next step */}
                {idx < STAGES.length - 1 && (
                  <div
                    className={`w-[2px] h-8 my-1 transition-colors duration-500 ${
                      idx < visualIndex ? 'bg-charcoal' : 'bg-charcoal/15'
                    }`}
                  />
                )}
              </div>

              {/* Step Label & Details */}
              <div
                className={`flex-1 transition-all duration-300 ${
                  isCurrent
                    ? 'p-3 bg-charcoal/5 border border-charcoal/20 rounded-md -mt-1 shadow-sm'
                    : isDone
                    ? 'pt-0.5 opacity-90'
                    : 'pt-0.5 opacity-40'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span
                    className={`text-sm ${
                      isCurrent
                        ? 'font-bold text-charcoal'
                        : isDone
                        ? 'font-medium text-charcoal'
                        : 'text-charcoal/70'
                    }`}
                  >
                    {s.label}
                  </span>

                  {/* Badges */}
                  {isDone && (
                    <span className="text-[11px] font-medium text-charcoal/70 flex items-center gap-1">
                      ✓ Done
                    </span>
                  )}
                  {isCurrent && (
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-charcoal text-ivory uppercase tracking-wider shadow-sm">
                      <span className="w-1.5 h-1.5 rounded-full bg-ivory animate-ping" />
                      In Progress
                    </span>
                  )}
                </div>

                <p
                  className={`text-xs mt-0.5 leading-relaxed ${
                    isCurrent ? 'text-charcoal/80 font-normal' : 'text-charcoal/60'
                  }`}
                >
                  {s.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Cancel action */}
      <div className="flex justify-center pt-2 border-t border-charcoal/10">
        <Button variant="secondary" onClick={onCancel} className="text-xs">
          Cancel Analysis
        </Button>
      </div>
    </div>
  );
}
