'use client'

import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import { ThemeProvider as NextThemeProvider } from 'next-themes'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

const theme = extendTheme({
  fonts: {
    heading: inter.style.fontFamily,
    body: inter.style.fontFamily,
  },
  colors: {
    brand: {
      50: '#e6fffd',
      100: '#b3f5f1',
      200: '#80ece4',
      300: '#4de2d7',
      400: '#1ad9cb',
      500: '#0d9488', // Main teal color
      600: '#0a7b71',
      700: '#08635a',
      800: '#054a43',
      900: '#03322c',
    },
    teal: {
      100: '#B2F5EA',
      200: '#81E6D9', // The specific blue-teal color requested (#81E6D9)
      300: '#81E6D9', // Update to match teal.200
      400: '#81E6D9', // Update to match teal.200
      500: '#0d9488', // Main teal color
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
    global: {
      body: {
        bg: 'gray.50',
        color: 'gray.900',
        _dark: {
          bg: 'navy.600', // Dark navy background like the sign-in page
          color: 'gray.50',
        },
      },
    },
  },
  semanticTokens: {
    colors: {
      primary: {
        default: 'brand.500',
        _dark: 'teal.200', // Light teal color for accents
      },
      secondary: {
        default: 'gray.800',
        _dark: 'teal.200',
      },
      accent: {
        default: 'brand.600',
        _dark: 'teal.200',
      },
      // Adding more semantic colors with opacity modifiers
      primaryAlpha: {
        default: 'brand.500/70',
        _dark: 'teal.200/70',
      },
      secondaryAlpha: {
        default: 'gray.800/70',
        _dark: 'teal.200/70',
      },
      bgSubtle: {
        default: 'gray.50',
        _dark: 'navy.500',
      },
      bgActive: {
        default: 'gray.100',
        _dark: 'navy.400',
      },
      cardBg: {
        default: 'white',
        _dark: 'navy.500', // Lighter navy for cards
      },
      borderColor: {
        default: 'gray.200',
        _dark: 'navy.400',
      },
      chartColor: {
        default: 'brand.500',
        _dark: 'teal.200', // The specific blue color for charts
      },
      statUpColor: {
        default: 'green.500',
        _dark: 'teal.200',
      },
    },
  },
})

export function Provider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemeProvider attribute="class">
      <ChakraProvider theme={theme}>{children}</ChakraProvider>
    </NextThemeProvider>
  )
} 