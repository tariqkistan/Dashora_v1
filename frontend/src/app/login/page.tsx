'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { setCookie } from 'cookies-next';
import { authService } from '@/services/api';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Alert,
  AlertIcon,
  useColorModeValue,
  Spinner,
  Center,
  Flex,
  Text,
  Card,
  CardBody,
  CardHeader,
  HStack,
  FormErrorMessage,
  useToast,
} from '@chakra-ui/react';
import { ColorModeButton } from '@/components/ui/color-mode';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const toast = useToast();

  // Only render UI after hydration to avoid mismatch
  useEffect(() => {
    setMounted(true);
    
    // Check if user is already authenticated
    const checkAuth = async () => {
      try {
        const user = await authService.checkAuth();
        if (user) {
          // User is already authenticated, redirect to dashboard
          router.push('/dashboard');
        }
      } catch (error) {
        // Authentication check failed, user needs to log in
        console.log('Auth check failed, user needs to login');
      }
    };
    
    checkAuth();
  }, [router]);

  const validateForm = () => {
    let isValid = true;
    
    // Reset errors
    setEmailError('');
    setPasswordError('');
    
    // Validate email
    if (!email) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Email is invalid');
      isValid = false;
    }
    
    // Validate password
    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    } else if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    }
    
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);

    try {
      const result = await authService.login(email, password);
      
      // Check if login was successful - our backend only returns a token
      if (result?.token) {
        // Login successful
        toast({
          title: 'Login successful',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        setError('Invalid response from server');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Failed to login');
      
      toast({
        title: 'Login failed',
        description: err.message || 'An error occurred during login',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // Show a loading state until client-side hydration is complete
  if (!mounted) {
    return (
      <Center h="100vh">
        <Spinner size="xl" color="brand.500" />
      </Center>
    );
  }

  return (
    <Box 
      minH="100vh" 
      display="flex" 
      alignItems="center" 
      flexDirection="column"
      bg={useColorModeValue('gray.50', 'gray.900')} 
      py={12} 
      px={4}
    >
      <Flex w="full" justifyContent="flex-end" px={4} mb={12}>
        <ColorModeButton />
      </Flex>
      
      <Container maxW="md">
        <Card
          rounded="lg"
          bg={useColorModeValue('white', 'gray.800')}
          boxShadow="lg"
          borderWidth="1px"
          borderColor={useColorModeValue('gray.200', 'gray.700')}
          overflow="hidden"
        >
          <CardHeader 
            borderBottomWidth="1px" 
            borderColor={useColorModeValue('gray.200', 'gray.700')}
            bg={useColorModeValue('white', 'gray.700')}
          >
            <Heading size="lg" textAlign="center" color={useColorModeValue('gray.800', 'white')}>
              Sign in to Dashora
            </Heading>
          </CardHeader>
          
          <CardBody as="form" onSubmit={handleSubmit} pt={6}>
            <Stack spacing={4}>
              <FormControl id="email" isRequired isInvalid={!!emailError}>
                <FormLabel>Email address</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) setEmailError('');
                  }}
                  bg={useColorModeValue('white', 'gray.800')}
                  borderColor={useColorModeValue('gray.300', 'gray.600')}
                  _hover={{
                    borderColor: useColorModeValue('gray.400', 'gray.500')
                  }}
                  _focus={{
                    borderColor: useColorModeValue('brand.500', 'teal.500'),
                    boxShadow: useColorModeValue('0 0 0 1px brand.500', '0 0 0 1px teal.500')
                  }}
                />
                <FormErrorMessage>{emailError}</FormErrorMessage>
              </FormControl>
              
              <FormControl id="password" isRequired isInvalid={!!passwordError}>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (passwordError) setPasswordError('');
                  }}
                  bg={useColorModeValue('white', 'gray.800')}
                  borderColor={useColorModeValue('gray.300', 'gray.600')}
                  _hover={{
                    borderColor: useColorModeValue('gray.400', 'gray.500')
                  }}
                  _focus={{
                    borderColor: useColorModeValue('brand.500', 'teal.500'),
                    boxShadow: useColorModeValue('0 0 0 1px brand.500', '0 0 0 1px teal.500')
                  }}
                />
                <FormErrorMessage>{passwordError}</FormErrorMessage>
              </FormControl>
              
              {error && (
                <Alert status="error" rounded="md">
                  <AlertIcon />
                  {error}
                </Alert>
              )}
              
              <Button
                type="submit"
                colorScheme="teal"
                size="lg"
                fontSize="md"
                isLoading={loading}
                loadingText="Signing in..."
                w="full"
                mt={4}
              >
                Sign in
              </Button>
            </Stack>
          </CardBody>
        </Card>
        
        <Text mt={6} textAlign="center" color={useColorModeValue('gray.600', 'gray.300')} fontSize="sm">
          {process.env.ENV === 'development' ? 
            'Demo credentials can be any email and password.' : 
            'Contact your administrator if you need access.'}
        </Text>
      </Container>
    </Box>
  );
} 