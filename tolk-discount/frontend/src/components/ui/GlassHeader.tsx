import React from 'react';
import { cn } from './GlassCard';

interface GlassHeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  actions?: React.ReactNode;
  className?: string;
  transparent?: boolean;
}

/**
 * GlassHeader - заголовок страницы с эффектом Liquid Glass
 * 
 * @example
 * ```tsx
 * <GlassHeader
 *   title="Профиль"
 *   subtitle="Личный кабинет пользователя"
 *   onBack={() => router.back()}
 *   actions={<SettingsButton />}
 * />
 * ```
 */
export function GlassHeader({
  title,
  subtitle,
  onBack,
  actions,
  className,
  transparent = false,
}: GlassHeaderProps) {
  return (
    <header
      className={cn(
        'sticky top-0 z-50',
        'backdrop-blur-xl',
        transparent ? 'bg-transparent' : 'bg-white/10',
        'border-b border-white/20',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Кнопка назад и заголовок */}
          <div className="flex items-center gap-4">
            {onBack && (
              <button
                onClick={onBack}
                className="p-2 -ml-2 rounded-xl hover:bg-white/10 transition-colors"
              >
                <svg
                  className="w-5 h-5 text-gray-700 dark:text-gray-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
            )}
            
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
                {title}
              </h1>
              {subtitle && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          
          {/* Действия справа */}
          {actions && (
            <div className="flex items-center gap-2">
              {actions}
            </div>
          )}
        </div>
      </div>
      
      {/* Декоративная линия сверху */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
    </header>
  );
}
