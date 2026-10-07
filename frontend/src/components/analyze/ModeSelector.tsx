import { EvidenceMode } from '../../types/api';

interface ModeSelectorProps {
  mode: EvidenceMode;
  onChange: (mode: EvidenceMode) => void;
}

export default function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <div className="space-y-2">
      <div className="flex flex-col sm:flex-row gap-4">
        <label className={`flex items-start space-x-3 cursor-pointer group p-3 rounded-md border transition-all ${mode === 'local' ? 'border-charcoal bg-charcoal/5 shadow-xs' : 'border-charcoal/20 hover:border-charcoal/40'}`}>
          <input
            type="radio"
            name="evidence-mode"
            value="local"
            checked={mode === 'local'}
            onChange={() => onChange('local')}
            className="w-4 h-4 mt-0.5 text-charcoal focus:ring-charcoal border-charcoal/40 bg-ivory accent-charcoal"
          />
          <div>
            <span className="block font-medium text-sm text-charcoal">Local Corpus (Default / Offline)</span>
            <span className="text-xs text-charcoal/60">Verified internal documents & benchmark (no API key needed)</span>
          </div>
        </label>

        <label className={`flex items-start space-x-3 cursor-pointer group p-3 rounded-md border transition-all ${mode === 'live' ? 'border-charcoal bg-charcoal/5 shadow-xs' : 'border-charcoal/20 hover:border-charcoal/40'}`}>
          <input
            type="radio"
            name="evidence-mode"
            value="live"
            checked={mode === 'live'}
            onChange={() => onChange('live')}
            className="w-4 h-4 mt-0.5 text-charcoal focus:ring-charcoal border-charcoal/40 bg-ivory accent-charcoal"
          />
          <div>
            <span className="block font-medium text-sm text-charcoal">Live Web Search</span>
            <span className="text-xs text-charcoal/60">Real-time web search (requires BRAVE_API_KEY in backend .env)</span>
          </div>
        </label>
      </div>

      {mode === 'live' && (
        <p className="text-[11px] text-charcoal/70 bg-charcoal/5 px-3 py-1.5 rounded border border-charcoal/10">
          Note: Live web search requires a free Brave Search API key configured in <code className="font-mono bg-charcoal/10 px-1 py-0.5 rounded">backend/.env</code>. For the built-in verified evidence corpus, select <strong>Local Corpus</strong>.
        </p>
      )}
    </div>
  );
}
