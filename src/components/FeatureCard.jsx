import React from 'react';
import { motion } from 'framer-motion';

/**
 * Reusable Glowing Feature Card Component
 * 
 * @param {Object} props
 * @param {string} props.title - Card title
 * @param {string} props.description - Card body description
 * @param {React.ReactNode} props.icon - Lucide icon component instance
 * @param {string} props.gradient - CSS linear-gradient string
 * @param {number} props.delay - Animation delay in seconds
 * @param {boolean} props.isDarkMode - Current theme state (dark vs light mode)
 * @param {string} [props.badge] - Optional badge label for custom cards
 */
export const FeatureCard = ({
  title,
  description,
  icon,
  gradient,
  delay = 0,
  isDarkMode = true,
  badge,
}) => {
  // Background-clip gradient border formula based on theme
  const foregroundBackgroundStyle = {
    background: isDarkMode
      ? `linear-gradient(#1A1A1C, #1A1A1C) padding-box, ${gradient} border-box`
      : `linear-gradient(#FFFFFF, #FFFFFF) padding-box, ${gradient} border-box`,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: 'easeOut', delay }}
      className="relative flex flex-col justify-start items-start w-full max-w-[260px] md:max-w-[300px] group mx-auto"
    >
      {/* GLOW BACKGROUND (CRUCIAL) */}
      <div
        className="absolute w-full h-[260px] md:h-[300px] opacity-60 rounded-[40px] pointer-events-none transition-opacity duration-500 group-hover:opacity-90"
        style={{
          background: gradient,
          filter: 'blur(45px)',
        }}
        aria-hidden="true"
      />

      {/* FOREGROUND CARD WITH GRADIENT BORDER (CRUCIAL) */}
      <div
        className={`self-stretch h-[260px] md:h-[300px] rounded-[40px] z-10 overflow-hidden border-[8px] border-transparent transition-all duration-500 ${
          isDarkMode ? 'shadow-2xl shadow-black/40' : 'shadow-xl shadow-slate-200/80'
        }`}
        style={foregroundBackgroundStyle}
      >
        {/* CONTENT INNER LAYOUT */}
        <div className="w-full h-full p-7 flex flex-col justify-between relative">
          
          {/* TOP HEADER: ICON & OPTIONAL BADGE */}
          <div className="flex items-center justify-between w-full">
            <div className={isDarkMode ? 'text-white/90' : 'text-slate-900'}>
              {React.cloneElement(icon, {
                size: 32,
                strokeWidth: 2.5,
              })}
            </div>
            {badge && (
              <span
                className={`text-[10px] font-semibold tracking-wider uppercase px-2.5 py-1 rounded-full border ${
                  isDarkMode
                    ? 'bg-white/10 text-white/90 border-white/20'
                    : 'bg-slate-900/10 text-slate-800 border-slate-900/20'
                }`}
              >
                {badge}
              </span>
            )}
          </div>

          {/* BOTTOM CONTENT: TITLE & DESCRIPTION */}
          <div className="mt-4">
            <h3
              className={`font-medium text-xl mb-3 tracking-tight transition-colors duration-300 ${
                isDarkMode ? 'text-white' : 'text-slate-900'
              }`}
            >
              {title}
            </h3>
            <p
              className={`text-[14px] leading-[1.6] font-normal selection:bg-white/20 transition-colors duration-300 ${
                isDarkMode ? 'text-gray-400' : 'text-slate-600'
              }`}
            >
              {description}
            </p>
          </div>

        </div>
      </div>
    </motion.div>
  );
};
