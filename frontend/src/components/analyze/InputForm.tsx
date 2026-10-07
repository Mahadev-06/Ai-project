import { useState } from 'react';
import Button from '../ui/Button';
import { AnalysisRequest } from '../../types/api';
import ExampleClaims from './ExampleClaims';
import { FileText, Globe } from 'lucide-react';

interface InputFormProps {
  onSubmit: (req: AnalysisRequest) => void;
  isLoading?: boolean;
}

export default function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'url'>('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const maxChars = 10000;

  const handleSubmit = () => {
    if (activeTab === 'text') {
      if (text.trim() && text.length <= maxChars) {
        onSubmit({ input_text: text.trim(), evidence_mode: 'auto' });
      }
    } else {
      if (url.trim()) {
        onSubmit({ input_url: url.trim(), evidence_mode: 'auto' });
      }
    }
  };

  const handleExampleSelect = (example: string) => {
    setActiveTab('text');
    setText(example);
  };

  const isSubmitDisabled =
    isLoading ||
    (activeTab === 'text' && (!text.trim() || text.length > maxChars)) ||
    (activeTab === 'url' && !url.trim());

  return (
    <div className="flex flex-col space-y-6">
      {/* Tabs */}
      <div className="flex border-b border-charcoal/10 gap-2">
        <button
          type="button"
          onClick={() => setActiveTab('text')}
          className={`flex items-center gap-2 px-4 py-2.5 font-medium text-sm transition-colors border-b-2 -mb-px focus-ring ${
            activeTab === 'text'
              ? 'border-charcoal text-charcoal'
              : 'border-transparent text-charcoal/60 hover:text-charcoal'
          }`}
          aria-selected={activeTab === 'text'}
          role="tab"
        >
          <FileText size={16} /> Text / Statements
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('url')}
          className={`flex items-center gap-2 px-4 py-2.5 font-medium text-sm transition-colors border-b-2 -mb-px focus-ring ${
            activeTab === 'url'
              ? 'border-charcoal text-charcoal'
              : 'border-transparent text-charcoal/60 hover:text-charcoal'
          }`}
          aria-selected={activeTab === 'url'}
          role="tab"
        >
          <Globe size={16} /> Web Article URL
        </button>
      </div>

      {/* Inputs */}
      {activeTab === 'text' ? (
        <div>
          <label htmlFor="claim-input" className="sr-only">
            Enter text or factual statements to analyze
          </label>
          <textarea
            id="claim-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste an article paragraph, news excerpt, or type one or more factual statements to investigate..."
            className="w-full h-44 p-4 bg-transparent border border-charcoal/20 rounded-md focus-ring resize-y text-charcoal placeholder-charcoal/40 text-base leading-relaxed"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
          <div className="flex justify-between items-center mt-2 text-xs text-charcoal/60">
            <span className={text.length > maxChars ? 'text-charcoal font-bold underline' : ''}>
              {text.length.toLocaleString()} / {maxChars.toLocaleString()} characters
            </span>
            <span className="hidden sm:inline">Ctrl + Enter to analyze</span>
          </div>
        </div>
      ) : (
        <div>
          <label htmlFor="url-input" className="block text-sm font-medium text-charcoal mb-2">
            Article or Webpage URL
          </label>
          <input
            id="url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.org/article-to-check"
            className="w-full p-3.5 bg-transparent border border-charcoal/20 rounded-md focus-ring text-charcoal placeholder-charcoal/40 text-base"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
          <p className="mt-2 text-xs text-charcoal/60">
            ClaimLens will safely fetch the page, isolate article paragraphs, and evaluate checkable claims.
          </p>
        </div>
      )}


      {/* Examples and Action */}
      <div className="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center pt-5 border-t border-charcoal/10 gap-4">
        <ExampleClaims onSelect={handleExampleSelect} />
        <Button
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="w-full sm:w-auto min-w-[140px]"
        >
          {isLoading ? 'Submitting...' : 'Analyze Evidence'}
        </Button>
      </div>
    </div>
  );
}
