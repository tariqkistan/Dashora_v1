'use client';

import { useTheme } from '@chakra-ui/react';
import React from 'react';

/**
 * A custom hook to get the raw color value from a Chakra UI theme token
 * Useful for components like Recharts that need raw color values
 */
export function useChakraColor(colorToken: string): string {
  const theme = useTheme();
  
  // Handle tokens in format 'color.shade'
  if (colorToken.includes('.')) {
    const [color, shade] = colorToken.split('.');
    
    // Handle opacity notation like 'teal.200/20'
    if (shade.includes('/')) {
      const [actualShade, opacity] = shade.split('/');
      const baseColor = theme.colors[color][actualShade];
      const opacityValue = parseInt(opacity) / 100;
      return `rgba(${hexToRgb(baseColor)}, ${opacityValue})`;
    }
    
    return theme.colors[color][shade];
  }
  
  // Handle direct color values (like hex codes)
  return colorToken;
}

/**
 * Convert hex to RGB for use in rgba() color values
 */
function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '0, 0, 0';
} 