import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Утилита для объединения классов
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

/**
 * GlassCard - компонент карточки с эффектом Liquid Glass
 * 
 * @example
 * ```tsx
 * <GlassCard padding="lg" hover>
 *   <h2>Заголовок</h2>
 *   <p>Содержимое карточки</p>
 * </GlassCard>
 * ```
 */
export function GlassCard({ 
  children, 
  className, 
  padding = 'md',
  hover = false,
  onClick 
}: GlassCardProps) {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      onClick={onClick}
      className={cn(
        // Базовые стили glassmorphism
        'relative backdrop-blur-xl bg-white/10',
        'border border-white/20',
        'rounded-2xl',
        'shadow-lg',
        'shadow-black/5',
        
        // Дополнительные эффекты
        'before:absolute before:inset-0 before:rounded-2xl',
        'before:bg-gradient-to-br before:from-white/10 before:to-transparent',
        'before:pointer-events-none',
        
        // Hover эффекты
        hover && 'cursor-pointer transition-all duration-300',
        hover && 'hover:shadow-xl hover:shadow-black/10',
        hover && 'hover:-translate-y-1',
        hover && 'hover:border-white/30',
        
        // Padding
        paddingClasses[padding],
        
        // Пользовательские классы
        className
      )}
    >
      {/* Блик сверху для эффекта стекла */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      
      {/* Контент */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
