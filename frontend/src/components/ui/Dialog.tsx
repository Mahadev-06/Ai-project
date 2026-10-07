import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export default function Dialog({ isOpen, onClose, title, children }: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      dialogRef.current?.focus();
      const handleEsc = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };
      window.addEventListener('keydown', handleEsc);
      return () => window.removeEventListener('keydown', handleEsc);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div className="fixed inset-0 bg-charcoal/50 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      <div 
        ref={dialogRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        className="relative bg-ivory rounded-lg shadow-xl w-full max-w-md p-6 border border-charcoal/10"
      >
        <div className="flex justify-between items-center mb-4">
          <h2 id="dialog-title" className="text-xl font-serif font-semibold text-charcoal">{title}</h2>
          <button onClick={onClose} className="text-charcoal/60 hover:text-charcoal p-2 rounded-full hover:bg-charcoal/5 focus-ring" aria-label="Close">
            <X size={20} />
          </button>
        </div>
        <div className="mt-2">
          {children}
        </div>
      </div>
    </div>
  );
}
