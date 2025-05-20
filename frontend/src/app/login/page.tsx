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
} from '@chakra-ui/react';
import { ColorModeButton } from '@/components/ui/color-mode';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Only render UI after hydration to avoid mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { token } = await authService.login(email, password);
      setCookie('auth_token', token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to login');
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
              <FormControl id="email" isRequired>
                <FormLabel>Email address</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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
          Demo credentials can be any email and password.
        </Text>
      </Container>
    </Box>
  );
} 