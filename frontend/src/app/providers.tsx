'use client';

import { ChakraProvider, ColorModeScript, extendTheme } from '@chakra-ui/react';
import { ThemeProvider } from 'next-themes';
import React from 'react';

// Define the theme
const theme = extendTheme({
  colors: {
    brand: {
      50: '#E6F6FF',
      100: '#BAE3FF',
      200: '#7CC4FA',
      300: '#47A3F3',
      400: '#2186EB',
      500: '#0967D2',
      600: '#0552B5',
      700: '#03449E',
      800: '#01337D',
      900: '#002159',
    },
    teal: {
      100: '#B2F5EA',
      200: '#81E6D9', // The specific blue-teal color for dark mode
      300: '#4FD1C5',
      400: '#38B2AC',
      500: '#0D9488',
    },
    navy: {
      50: '#E2E8F0',
      100: '#CBD5E0',
      200: '#A0AEC0',
      300: '#718096',
      400: '#4A5568',
      500: '#2D3748', // Card background
      600: '#1A202C', // Main background
      700: '#171923',
      800: '#0E1116',
      900: '#05070A',
    }
  },
  config: {
    initialColorMode: 'system',
    useSystemColorMode: true,
  },
  styles: {
    global: (props: { colorMode: string }) => ({
      body: {
        bg: props.colorMode === 'dark' ? '#171923' : 'gray.50',
        color: props.colorMode === 'dark' ? 'gray.100' : 'gray.900',
      },
    }),
  },
  semanticTokens: {
    colors: {
      primary: {
        default: 'brand.500',
        _dark: 'teal.200',
      },
      cardBg: {
        default: 'white',
        _dark: '#171923',
      },
      borderColor: {
        default: 'gray.200',
        _dark: 'gray.700',
      },
      chartColor: {
        default: 'brand.500',
        _dark: 'teal.200',
      },
    }
  }
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <ChakraProvider theme={theme}>
        <ThemeProvider attribute="class">
          {children}
        </ThemeProvider>
      </ChakraProvider>
    </>
  );
} 