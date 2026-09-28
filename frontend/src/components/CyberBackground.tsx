import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export const CyberBackground: React.FC = () => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-[#0B0F19]">
      {/* Layer 1: High-Tech Subtle Grid */}
      <div 
        className="absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage: `
            linear-gradient(to right, #ffffff 1px, transparent 1px),
            linear-gradient(to bottom, #ffffff 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px'
        }}
      />

      {/* Layer 2: Ambient Radial Glows */}
      <div className="absolute -top-[20%] left-1/2 -translate-x-1/2 w-[900px] h-[500px] rounded-full bg-gradient-to-b from-indigo-500/10 via-cyan-500/5 to-transparent blur-3xl" />
      <div className="absolute top-[40%] -right-[15%] w-[600px] h-[600px] rounded-full bg-gradient-to-tl from-cyan-600/5 via-blue-500/5 to-transparent blur-3xl" />
      <div className="absolute -bottom-[10%] left-[5%] w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-indigo-600/5 to-transparent blur-3xl" />

      {/* Layer 3: Floating Network Nodes (Subtle & GPU-friendly) */}
      {!shouldReduceMotion && (
        <>
          <motion.div
            className="absolute top-1/4 left-[15%] w-1.5 h-1.5 rounded-full bg-cyan-400/30"
            animate={{
              y: [-10, 15, -10],
              opacity: [0.2, 0.5, 0.2]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute top-1/3 right-[20%] w-2 h-2 rounded-full bg-indigo-400/25"
            animate={{
              y: [15, -12, 15],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-1/4 left-[35%] w-1 h-1 rounded-full bg-cyan-300/40"
            animate={{
              x: [-10, 10, -10],
              opacity: [0.15, 0.45, 0.15]
            }}
            transition={{
              duration: 9,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </>
      )}

      {/* Subtle Vignette Border */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#0B0F19] via-transparent to-transparent opacity-80" />
    </div>
  );
};
