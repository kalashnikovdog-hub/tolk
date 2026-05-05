import React from 'react';
import { cn } from './GlassCard';

interface GlassButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
}

/**
 * GlassButton - кнопка с эффектом Liquid Glass
 * 
 * @example
 * ```tsx
 * <GlassButton variant="primary" onClick={handleClick}>
 *   Нажать меня
 * </GlassButton>
 * ```
 */
export function GlassButton({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  className,
  fullWidth = false,
}: GlassButtonProps) {
  const baseStyles = `
    relative overflow-hidden
    backdrop-blur-xl
    border rounded-xl
    font-semibold
    transition-all duration-300
    flex items-center justify-center gap-2
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
  `;

  const variants = {
    primary: `
      bg-blue-500/20 hover:bg-blue-500/30
      border-blue-400/30 hover:border-blue-400/50
      text-blue-600 dark:text-blue-400
      shadow-lg shadow-blue-500/20
      hover:shadow-xl hover:shadow-blue-500/30
      hover:-translate-y-0.5
      focus:ring-blue-500
    `,
    secondary: `
      bg-gray-500/20 hover:bg-gray-500/30
      border-gray-400/30 hover:border-gray-400/50
      text-gray-700 dark:text-gray-300
      shadow-lg shadow-gray-500/10
      hover:shadow-xl hover:shadow-gray-500/20
      hover:-translate-y-0.5
      focus:ring-gray-500
    `,
    danger: `
      bg-red-500/20 hover:bg-red-500/30
      border-red-400/30 hover:border-red-400/50
      text-red-600 dark:text-red-400
      shadow-lg shadow-red-500/20
      hover:shadow-xl hover:shadow-red-500/30
      hover:-translate-y-0.5
      focus:ring-red-500
    `,
    ghost: `
      bg-transparent hover:bg-white/10
      border-transparent hover:border-white/20
      text-gray-700 dark:text-gray-300
      hover:-translate-y-0
      focus:ring-gray-500
    `,
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
    >
      {/* Градиентный overlay для эффекта стекла */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
      
      {/* Контент */}
      <span className="relative z-10 flex items-center gap-2">
        {loading ? (
          <svg
            className="animate-spin h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          icon
        )}
        {children}
      </span>
    </button>
  );
}
