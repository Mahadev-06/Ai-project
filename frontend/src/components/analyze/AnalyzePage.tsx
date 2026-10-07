import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InputForm from './InputForm';
import { AnalysisRequest } from '../../types/api';
import { apiClient } from '../../api/client';
import { AlertCircle } from 'lucide-react';

export default function AnalyzePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (req: AnalysisRequest) => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.submitAnalysis(req);
      navigate(`/results/${res.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit analysis. Please check your network or backend.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10 flex flex-col items-center">
      <div className="text-center mb-10">
        <h1 className="text-4xl sm:text-5xl font-serif font-bold text-charcoal mb-4 tracking-tight">
          Check the claim. Read the evidence.
        </h1>
        <p className="text-base sm:text-lg text-charcoal/70 max-w-2xl mx-auto leading-relaxed">
          Explore factual statements with transparent citations, cross-encoder natural language inference,
          and documented source credibility signals.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="w-full mb-6 p-4 border border-charcoal bg-charcoal/5 rounded-md flex items-start gap-3 text-sm text-charcoal"
        >
          <AlertCircle size={18} className="mt-0.5 shrink-0" />
          <div className="flex-1">
            <span className="font-semibold">Unable to process request:</span> {error}
          </div>
        </div>
      )}

      <div className="w-full bg-ivory p-6 sm:p-8 rounded-lg border border-charcoal/15 shadow-sm">
        <InputForm onSubmit={handleAnalyze} isLoading={loading} />
      </div>
    </div>
  );
}
