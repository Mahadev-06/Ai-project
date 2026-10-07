import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
}

export default function Button({ variant = 'primary', children, className = '', ...props }: ButtonProps) {
  let styles = '';
  switch (variant) {
    case 'primary':
      styles = 'bg-charcoal text-ivory hover:bg-charcoal/90';
      break;
    case 'secondary':
      styles = 'border border-charcoal text-charcoal hover:bg-charcoal/5';
      break;
    case 'ghost':
      styles = 'text-charcoal hover:bg-charcoal/10';
      break;
  }

  return (
    <button
      className={`px-4 py-2 min-h-[44px] min-w-[44px] rounded-md font-medium transition-colors focus-ring disabled:opacity-50 disabled:cursor-not-allowed ${styles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
