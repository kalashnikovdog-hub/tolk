import React, { forwardRef } from 'react';
import { cn } from './GlassCard';

interface GlassTextFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  rightElement?: React.ReactNode;
}

/**
 * GlassTextField - текстовое поле с эффектом Liquid Glass
 * 
 * @example
 * ```tsx
 * <GlassTextField
 *   label="Email"
 *   type="email"
 *   placeholder="user@example.com"
 *   icon={<MailIcon />}
 * />
 * ```
 */
export const GlassTextField = forwardRef<HTMLInputElement, GlassTextFieldProps>(
  ({ label, error, icon, rightElement, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {label}
          </label>
        )}
        
        <div className="relative">
          {/* Контейнер с эффектом стекла */}
          <div
            className={cn(
              'relative overflow-hidden',
              'backdrop-blur-xl bg-white/10',
              'border rounded-xl',
              'transition-all duration-300',
              
              // Состояния borders
              error
                ? 'border-red-400/50 focus-within:border-red-500/70'
                : 'border-white/20 focus-within:border-blue-400/50',
              
              // Тени
              'shadow-lg shadow-black/5',
              'focus-within:shadow-xl focus-within:shadow-blue-500/10',
              
              className
            )}
          >
            {/* Градиентный overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
            
            {/* Иконка слева */}
            {icon && (
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 z-10">
                {icon}
              </div>
            )}
            
            {/* Input поле */}
            <input
              ref={ref}
              className={cn(
                'relative z-10 w-full bg-transparent',
                'text-gray-900 dark:text-white placeholder-gray-400',
                'focus:outline-none',
                
                // Padding в зависимости от наличия иконки
                icon ? 'pl-12 pr-4' : 'px-4',
                rightElement ? 'pr-12' : '',
                
                'py-3.5 text-base'
              )}
              {...props}
            />
            
            {/* Элемент справа (например, кнопка показать пароль) */}
            {rightElement && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10">
                {rightElement}
              </div>
            )}
          </div>
        </div>
        
        {/* Сообщение об ошибке */}
        {error && (
          <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            {error}
          </p>
        )}
      </div>
    );
  }
);

GlassTextField.displayName = 'GlassTextField';
