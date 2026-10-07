export default function Spinner({ size = 24 }: { size?: number }) {
  return (
    <div 
      className="inline-block border-2 border-charcoal/20 border-t-charcoal rounded-full animate-spin"
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  );
}
