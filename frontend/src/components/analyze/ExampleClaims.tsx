import { Lightbulb } from 'lucide-react';

interface ExampleClaimsProps {
  onSelect: (claim: string) => void;
}

const examples = [
  'The Great Wall of China is visible from space with the naked eye.',
  'Water boils at 100 degrees Celsius at sea level.',
  'The Earth revolves around the Sun once every 365.25 days.',
  'Lightning never strikes the same place twice.',
  'Mount Everest is the tallest mountain on Earth.'
];

export default function ExampleClaims({ onSelect }: ExampleClaimsProps) {
  return (
    <div className="flex items-center space-x-2 text-sm">
      <Lightbulb className="w-4 h-4 text-charcoal/60" />
      <span className="text-charcoal/60">Try:</span>
      <div className="flex flex-wrap gap-2">
        {examples.map((ex, i) => (
          <button
            key={i}
            onClick={() => onSelect(ex)}
            title={ex}
            className="text-xs px-2 py-1 rounded border border-charcoal/20 hover:border-charcoal hover:bg-charcoal/5 text-charcoal focus-ring transition-colors"
          >
            Example {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}
