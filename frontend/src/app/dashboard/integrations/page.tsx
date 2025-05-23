'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  Flex,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Stack,
  FormControl,
  FormLabel,
  Input,
  Switch,
  HStack,
  Divider,
  Badge,
  useColorModeValue,
  useToast,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Icon,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormErrorMessage,
  ButtonGroup,
} from '@chakra-ui/react';
import { domainService } from '@/services/api';
import { AddIcon } from '@chakra-ui/icons';

interface Domain {
  domain: string;
  name: string;
  woocommerce_enabled: boolean;
  ga_enabled: boolean;
}

interface WooCommerceConnection {
  url: string;
  key: string;
  secret: string;
  connected: boolean;
  store_name?: string;
  total_orders?: number;
  current_revenue?: {
    amount: number;
    currency: string;
    from_orders: number;
  };
  top_products?: Array<{
    name: string;
    total_sales: number;
    price: number;
    image: string;
    sku: string;
    stock_status: string;
  }>;
  store_info?: {
    currency: string;
    country: string;
    domain: string;
  };
  last_updated?: string;
}

interface GoogleAnalyticsConnection {
  measurementId: string;
  apiSecret: string;
  connected: boolean;
}

interface IntegrationState {
  [key: string]: {
    woocommerce: WooCommerceConnection;
    googleAnalytics: GoogleAnalyticsConnection;
  };
}

interface NewDomainForm {
  name: string;
  domain: string;
  woocommerce: {
    key: string;
    secret: string;
    enabled: boolean;
  };
  googleAnalytics: {
    measurementId: string;
    apiSecret: string;
    enabled: boolean;
  };
}

export default function IntegrationsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectionLoading, setConnectionLoading] = useState<{[key: string]: boolean}>({});
  const [error, setError] = useState('');
  const [integrationState, setIntegrationState] = useState<IntegrationState>({});
  const toast = useToast();
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newDomain, setNewDomain] = useState<NewDomainForm>({
    name: '',
    domain: '',
    woocommerce: {
      key: '',
      secret: '',
      enabled: false
    },
    googleAnalytics: {
      measurementId: '',
      apiSecret: '',
      enabled: false
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState<{[key: string]: string}>({});
  
  const bgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.700', 'white');
  const panelBg = useColorModeValue('gray.50', 'gray.800');
  const successBg = useColorModeValue('green.50', 'green.900');
  const modalBg = useColorModeValue('white', 'gray.800');
  
  const fetchDomains = async () => {
    try {
      setLoading(true);
      const { domains } = await domainService.getDomains();
      setDomains(domains);
      
      // Initialize state with existing integration data from domains
      const initialState: IntegrationState = {};
      domains.forEach((domain: Domain) => {
        initialState[domain.domain] = {
          woocommerce: {
            url: domain.domain,
            key: '',
            secret: '',
            connected: domain.woocommerce_enabled,
            store_name: domain.woocommerce_enabled ? domain.name : undefined,
          },
          googleAnalytics: {
            measurementId: '',
            apiSecret: '',
            connected: domain.ga_enabled
          }
        };
      });
      
      setIntegrationState(initialState);
      
      // For domains with enabled WooCommerce, fetch additional connection details
      for (const domain of domains) {
        if (domain.woocommerce_enabled) {
          try {
            // Get connection details if WooCommerce is already enabled
            const details = await domainService.getIntegrationDetails(domain.domain, 'woocommerce');
            
            if (details) {
              setIntegrationState(prev => ({
                ...prev,
                [domain.domain]: {
                  ...(prev[domain.domain] || {}),
                  woocommerce: {
                    ...(prev[domain.domain]?.woocommerce || {}),
                    ...details,
                    connected: true
                  }
                }
              }));
            }
          } catch (err) {
            console.error(`Error fetching WooCommerce details for ${domain.domain}:`, err);
          }
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch domains');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);
  
  const handleWooCommerceChange = (domain: string, field: string, value: string | boolean) => {
    setIntegrationState(prev => ({
      ...prev,
      [domain]: {
        ...prev[domain],
        woocommerce: {
          ...prev[domain].woocommerce,
          [field]: value
        }
      }
    }));
  };
  
  const handleGoogleAnalyticsChange = (domain: string, field: string, value: string | boolean) => {
    setIntegrationState(prev => ({
      ...prev,
      [domain]: {
        ...prev[domain],
        googleAnalytics: {
          ...prev[domain].googleAnalytics,
          [field]: value
        }
      }
    }));
  };
  
  const handleConnectWooCommerce = async (domain: string) => {
    const integration = integrationState[domain].woocommerce;
    
    setConnectionLoading(prev => ({...prev, [domain]: true}));
    
    try {
      // Prepare the credentials to connect
      const credentials = {
        domain: integration.url || domain, // Use the provided URL or domain name
        consumer_key: integration.key,
        consumer_secret: integration.secret
      };
      
      // Call API to connect WooCommerce
      const result = await domainService.connectIntegration(domain, 'woocommerce', credentials);
      
      if (result.success) {
        // Update state with connected status and store details
        setIntegrationState(prev => ({
          ...prev,
          [domain]: {
            ...prev[domain],
            woocommerce: {
              ...prev[domain].woocommerce,
              connected: true,
              store_name: result.store_name || prev[domain].woocommerce.store_name,
              product_count: result.product_count,
              last_order_date: result.last_order_date
            }
          }
        }));
        
        toast({
          title: 'WooCommerce Connected',
          description: `Successfully connected ${domain} to WooCommerce`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } else {
        throw new Error(result.error || 'Failed to connect WooCommerce');
      }
    } catch (err: any) {
      console.error('WooCommerce connection error:', err);
      toast({
        title: 'Connection Failed',
        description: err.message || 'Could not connect to WooCommerce. Please check your credentials.',
        status: 'error',
        duration: 7000,
        isClosable: true,
      });
    } finally {
      setConnectionLoading(prev => ({...prev, [domain]: false}));
    }
  };
  
  const handleDisconnectWooCommerce = async (domain: string) => {
    setConnectionLoading(prev => ({...prev, [domain]: true}));
    
    try {
      // Call API to disconnect WooCommerce
      const result = await domainService.disconnectIntegration(domain, 'woocommerce');
      
      if (result.success) {
        // Update state with disconnected status
        setIntegrationState(prev => ({
          ...prev,
          [domain]: {
            ...prev[domain],
            woocommerce: {
              url: domain,
              key: '',
              secret: '',
              connected: false,
              store_name: undefined,
              product_count: undefined,
              last_order_date: undefined
            }
          }
        }));
        
        toast({
          title: 'WooCommerce Disconnected',
          description: `Successfully disconnected ${domain} from WooCommerce`,
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
      } else {
        throw new Error(result.error || 'Failed to disconnect WooCommerce');
      }
    } catch (err: any) {
      console.error('WooCommerce disconnection error:', err);
      toast({
        title: 'Disconnection Failed',
        description: err.message || 'Could not disconnect from WooCommerce',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setConnectionLoading(prev => ({...prev, [domain]: false}));
    }
  };
  
  const handleConnect = (domain: string, integrationType: 'woocommerce' | 'googleAnalytics') => {
    if (integrationType === 'woocommerce') {
      handleConnectWooCommerce(domain);
    } else {
      // Handle Google Analytics connection
      const integration = integrationState[domain][integrationType];
      
      // Simulated GA connection for now
      setIntegrationState(prev => ({
        ...prev,
        [domain]: {
          ...prev[domain],
          [integrationType]: {
            ...prev[domain][integrationType],
            connected: true
          }
        }
      }));
      
      toast({
        title: 'Google Analytics Connected',
        description: `Successfully connected ${domain} to Google Analytics`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleDisconnect = (domain: string, integrationType: 'woocommerce' | 'googleAnalytics') => {
    if (integrationType === 'woocommerce') {
      handleDisconnectWooCommerce(domain);
    } else {
      // Handle Google Analytics disconnection
      setIntegrationState(prev => ({
        ...prev,
        [domain]: {
          ...prev[domain],
          [integrationType]: {
            ...prev[domain][integrationType],
            connected: false
          }
        }
      }));
      
      toast({
        title: 'Google Analytics Disconnected',
        description: `Successfully disconnected ${domain} from Google Analytics`,
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleNewDomainChange = (field: string, value: string) => {
    setNewDomain(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field if it exists
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = {...prev};
        delete newErrors[field];
        return newErrors;
      });
    }
  };
  
  const handleIntegrationToggle = (integration: 'woocommerce' | 'googleAnalytics', enabled: boolean) => {
    setNewDomain(prev => ({
      ...prev,
      [integration]: {
        ...prev[integration],
        enabled
      }
    }));
  };
  
  const handleIntegrationFieldChange = (integration: 'woocommerce' | 'googleAnalytics', field: string, value: string) => {
    setNewDomain(prev => ({
      ...prev,
      [integration]: {
        ...prev[integration],
        [field]: value
      }
    }));
    
    // Clear error for this field if it exists
    const errorKey = `${integration}.${field}`;
    if (formErrors[errorKey]) {
      setFormErrors(prev => {
        const newErrors = {...prev};
        delete newErrors[errorKey];
        return newErrors;
      });
    }
  };
  
  const validateForm = (): boolean => {
    const errors: {[key: string]: string} = {};
    
    if (!newDomain.name.trim()) {
      errors.name = 'Store name is required';
    }
    
    if (!newDomain.domain.trim()) {
      errors.domain = 'Domain is required';
    } else {
      // Extract the domain from URL if it contains http:// or https://
      let domainValue = newDomain.domain.trim();
      try {
        // Check if it's a URL with protocol
        if (domainValue.startsWith('http://') || domainValue.startsWith('https://')) {
          const url = new URL(domainValue);
          domainValue = url.hostname;
        }
        
        // Now validate the extracted domain with a more permissive regex
        if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z0-9][a-zA-Z0-9-]*)+$/.test(domainValue)) {
          errors.domain = 'Please enter a valid domain (e.g., example.com)';
        }
      } catch (e) {
        errors.domain = 'Please enter a valid domain or URL';
      }
    }
    
    if (newDomain.woocommerce.enabled) {
      if (!newDomain.woocommerce.key.trim()) {
        errors['woocommerce.key'] = 'WooCommerce API key is required';
      }
      if (!newDomain.woocommerce.secret.trim()) {
        errors['woocommerce.secret'] = 'WooCommerce API secret is required';
      }
    }
    
    if (newDomain.googleAnalytics.enabled) {
      if (!newDomain.googleAnalytics.measurementId.trim()) {
        errors['googleAnalytics.measurementId'] = 'Google Analytics measurement ID is required';
      }
      if (!newDomain.googleAnalytics.apiSecret.trim()) {
        errors['googleAnalytics.apiSecret'] = 'Google Analytics API secret is required';
      }
    }
    
    if (!newDomain.woocommerce.enabled && !newDomain.googleAnalytics.enabled) {
      errors.integration = 'At least one integration must be enabled';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleAddWebsite = async () => {
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Extract domain from URL if needed
      let domainValue = newDomain.domain.trim();
      try {
        if (domainValue.startsWith('http://') || domainValue.startsWith('https://')) {
          const url = new URL(domainValue);
          domainValue = url.hostname;
        }
      } catch (e) {
        console.error('Error parsing domain URL:', e);
        // Keep the original value if parsing fails
      }
      
      // Add domain to the system
      const result = await domainService.addDomain({
        name: newDomain.name.trim(),
        domain: domainValue,
        woocommerce_enabled: newDomain.woocommerce.enabled,
        ga_enabled: newDomain.googleAnalytics.enabled
      });
      
      if (result.success) {
        // Connect integrations if enabled
        const domainId = result.domain_id || domainValue;
        
        // Connect WooCommerce if enabled
        if (newDomain.woocommerce.enabled) {
          try {
            await domainService.connectIntegration(domainId, 'woocommerce', {
              domain: domainValue,
              consumer_key: newDomain.woocommerce.key.trim(),
              consumer_secret: newDomain.woocommerce.secret.trim()
            });
          } catch (err) {
            console.error('Error connecting WooCommerce:', err);
            toast({
              title: 'WooCommerce Connection Error',
              description: 'The domain was added but there was an error connecting WooCommerce. Please try connecting it manually.',
              status: 'warning',
              duration: 5000,
              isClosable: true,
            });
          }
        }
        
        // Connect Google Analytics if enabled
        if (newDomain.googleAnalytics.enabled) {
          try {
            await domainService.connectIntegration(domainId, 'googleanalytics', {
              measurementId: newDomain.googleAnalytics.measurementId.trim(),
              apiSecret: newDomain.googleAnalytics.apiSecret.trim()
            });
          } catch (err) {
            console.error('Error connecting Google Analytics:', err);
            toast({
              title: 'Google Analytics Connection Error',
              description: 'The domain was added but there was an error connecting Google Analytics. Please try connecting it manually.',
              status: 'warning',
              duration: 5000,
              isClosable: true,
            });
          }
        }
        
        // Refresh the domains list
        await fetchDomains();
        
        // Show success message
        toast({
          title: 'Website Added Successfully',
          description: `${newDomain.name} has been added to your dashboard.`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        // Reset form and close modal
        setNewDomain({
          name: '',
          domain: '',
          woocommerce: {
            key: '',
            secret: '',
            enabled: false
          },
          googleAnalytics: {
            measurementId: '',
            apiSecret: '',
            enabled: false
          }
        });
        onClose();
      } else {
        throw new Error(result.error || 'Unknown error adding domain');
      }
    } catch (err: any) {
      console.error('Error adding domain:', err);
      toast({
        title: 'Error Adding Website',
        description: err.message || 'An error occurred while adding the website. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box maxW="1400px" mx="auto" py={20} textAlign="center">
        <Spinner size="xl" thickness="4px" speed="0.65s" color="teal.500" />
        <Text mt={4}>Loading integrations...</Text>
      </Box>
    );
  }

  return (
    <Box maxW="1400px" mx="auto" py={5} px={{ base: 2, sm: 4, md: 6 }}>
      <Flex mb={6} justifyContent="space-between" alignItems="center">
        <Heading size="lg" color={headingColor}>
          Integrations
        </Heading>
        <Button 
          leftIcon={<AddIcon />} 
          colorScheme="teal" 
          onClick={onOpen}
          size="md"
        >
          Add Website
        </Button>
      </Flex>
      
      <Text mb={8} color={textColor}>
        Connect your domains to WooCommerce and Google Analytics to enable data synchronization and comprehensive analytics.
      </Text>
      
      {error && (
        <Alert status="error" mb={6} borderRadius="md">
          <AlertIcon />
          <AlertTitle mr={2}>Error:</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent bg={modalBg}>
          <ModalHeader>Add New Website</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl isRequired isInvalid={!!formErrors.name}>
                <FormLabel>Store Name</FormLabel>
                <Input 
                  placeholder="My Online Store" 
                  value={newDomain.name}
                  onChange={(e) => handleNewDomainChange('name', e.target.value)}
                />
                {formErrors.name && <FormErrorMessage>{formErrors.name}</FormErrorMessage>}
              </FormControl>
              
              <FormControl isRequired isInvalid={!!formErrors.domain}>
                <FormLabel>Domain</FormLabel>
                <Input 
                  placeholder="example.com or https://example.com" 
                  value={newDomain.domain}
                  onChange={(e) => handleNewDomainChange('domain', e.target.value)}
                />
                {formErrors.domain && <FormErrorMessage>{formErrors.domain}</FormErrorMessage>}
              </FormControl>
              
              <Divider my={2} />
              
              <FormControl display="flex" alignItems="center" mb={2}>
                <FormLabel htmlFor="woocommerce-toggle" mb="0">
                  Enable WooCommerce
                </FormLabel>
                <Switch 
                  id="woocommerce-toggle" 
                  colorScheme="teal"
                  isChecked={newDomain.woocommerce.enabled}
                  onChange={(e) => handleIntegrationToggle('woocommerce', e.target.checked)}
                />
              </FormControl>
              
              {newDomain.woocommerce.enabled && (
                <Box pl={4} borderLeft="2px" borderColor="teal.200" py={2}>
                  <FormControl isRequired isInvalid={!!formErrors['woocommerce.key']} mb={3}>
                    <FormLabel>WooCommerce API Key</FormLabel>
                    <Input 
                      placeholder="ck_xxxxxxxxxxxxxxxxxxxx" 
                      value={newDomain.woocommerce.key}
                      onChange={(e) => handleIntegrationFieldChange('woocommerce', 'key', e.target.value)}
                    />
                    {formErrors['woocommerce.key'] && <FormErrorMessage>{formErrors['woocommerce.key']}</FormErrorMessage>}
                  </FormControl>
                  
                  <FormControl isRequired isInvalid={!!formErrors['woocommerce.secret']}>
                    <FormLabel>WooCommerce API Secret</FormLabel>
                    <Input 
                      placeholder="cs_xxxxxxxxxxxxxxxxxxxx" 
                      type="password"
                      value={newDomain.woocommerce.secret}
                      onChange={(e) => handleIntegrationFieldChange('woocommerce', 'secret', e.target.value)}
                    />
                    {formErrors['woocommerce.secret'] && <FormErrorMessage>{formErrors['woocommerce.secret']}</FormErrorMessage>}
                  </FormControl>
                </Box>
              )}
              
              <Divider my={2} />
              
              <FormControl display="flex" alignItems="center" mb={2}>
                <FormLabel htmlFor="ga-toggle" mb="0">
                  Enable Google Analytics
                </FormLabel>
                <Switch 
                  id="ga-toggle" 
                  colorScheme="teal"
                  isChecked={newDomain.googleAnalytics.enabled}
                  onChange={(e) => handleIntegrationToggle('googleAnalytics', e.target.checked)}
                />
              </FormControl>
              
              {newDomain.googleAnalytics.enabled && (
                <Box pl={4} borderLeft="2px" borderColor="teal.200" py={2}>
                  <FormControl isRequired isInvalid={!!formErrors['googleAnalytics.measurementId']} mb={3}>
                    <FormLabel>Google Analytics Measurement ID</FormLabel>
                    <Input 
                      placeholder="G-XXXXXXXXXX" 
                      value={newDomain.googleAnalytics.measurementId}
                      onChange={(e) => handleIntegrationFieldChange('googleAnalytics', 'measurementId', e.target.value)}
                    />
                    {formErrors['googleAnalytics.measurementId'] && <FormErrorMessage>{formErrors['googleAnalytics.measurementId']}</FormErrorMessage>}
                  </FormControl>
                  
                  <FormControl isRequired isInvalid={!!formErrors['googleAnalytics.apiSecret']}>
                    <FormLabel>Google Analytics API Secret</FormLabel>
                    <Input 
                      placeholder="API Secret from Google Analytics" 
                      type="password"
                      value={newDomain.googleAnalytics.apiSecret}
                      onChange={(e) => handleIntegrationFieldChange('googleAnalytics', 'apiSecret', e.target.value)}
                    />
                    {formErrors['googleAnalytics.apiSecret'] && <FormErrorMessage>{formErrors['googleAnalytics.apiSecret']}</FormErrorMessage>}
                  </FormControl>
                </Box>
              )}
              
              {formErrors.integration && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertDescription>{formErrors.integration}</AlertDescription>
                </Alert>
              )}
            </Stack>
          </ModalBody>
          
          <ModalFooter>
            <ButtonGroup spacing={3}>
              <Button variant="outline" onClick={onClose} isDisabled={isSubmitting}>
                Cancel
              </Button>
              <Button 
                colorScheme="teal" 
                onClick={handleAddWebsite} 
                isLoading={isSubmitting}
                loadingText="Adding..."
              >
                Add Website
              </Button>
            </ButtonGroup>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {domains.length === 0 ? (
        <Card bg={bgColor} borderColor={borderColor} shadow="sm">
          <CardBody>
            <Text>No domains found. Please add a domain first.</Text>
          </CardBody>
        </Card>
      ) : (
        domains.map(domain => (
          <Card 
            key={domain.domain} 
            mb={8} 
            bg={bgColor} 
            borderColor={borderColor} 
            borderWidth="1px" 
            shadow="sm"
          >
            <CardHeader pb={2}>
              <Flex justify="space-between" align="center">
                <Heading size="md" color={headingColor}>
                  {domain.name}
                </Heading>
                <Text color={textColor} fontSize="sm">
                  {domain.domain}
                </Text>
              </Flex>
            </CardHeader>
            
            <Divider borderColor={borderColor} />
            
            <CardBody>
              <Tabs variant="enclosed" colorScheme="teal">
                <TabList>
                  <Tab>WooCommerce</Tab>
                  <Tab>Google Analytics</Tab>
                </TabList>
                
                <TabPanels>
                  <TabPanel p={4} bg={panelBg} borderRadius="md" mt={4}>
                    <Stack spacing={4}>
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Heading size="sm" mb={1}>WooCommerce Integration</Heading>
                          <Text fontSize="sm" color={textColor}>
                            Connect your WooCommerce store to import orders and revenue data.
                          </Text>
                        </Box>
                        <HStack>
                          {integrationState[domain.domain]?.woocommerce.connected ? (
                            <Badge colorScheme="green" p={2} borderRadius="md">
                              Connected
                            </Badge>
                          ) : (
                            <Badge colorScheme="gray" p={2} borderRadius="md">
                              Not Connected
                            </Badge>
                          )}
                        </HStack>
                      </Flex>
                      
                      <Divider borderColor={borderColor} />
                      
                      {integrationState[domain.domain]?.woocommerce.connected ? (
                        <Box p={4} bg={successBg} borderRadius="md">
                          <Heading size="sm" mb={3}>Connected WooCommerce Store</Heading>
                          
                          {/* Store Overview */}
                          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={6}>
                            <Box>
                              <Text fontWeight="bold" fontSize="sm" color="gray.600">Store Name</Text>
                              <Text fontSize="lg" fontWeight="semibold">
                                {integrationState[domain.domain]?.woocommerce?.store_name || domain.name}
                              </Text>
                            </Box>
                            
                            <Box>
                              <Text fontWeight="bold" fontSize="sm" color="gray.600">Total Orders</Text>
                              <Text fontSize="lg" fontWeight="semibold">
                                {integrationState[domain.domain]?.woocommerce?.total_orders?.toLocaleString() || '0'}
                              </Text>
                            </Box>
                            
                            <Box>
                              <Text fontWeight="bold" fontSize="sm" color="gray.600">Current Revenue</Text>
                              <Text fontSize="lg" fontWeight="semibold">
                                {integrationState[domain.domain]?.woocommerce?.current_revenue ? 
                                  `${integrationState[domain.domain]?.woocommerce?.current_revenue?.currency} ${integrationState[domain.domain]?.woocommerce?.current_revenue?.amount?.toLocaleString()}` 
                                  : 'N/A'
                                }
                              </Text>
                              {integrationState[domain.domain]?.woocommerce?.current_revenue?.from_orders && (
                                <Text fontSize="xs" color="gray.500">
                                  From {integrationState[domain.domain]?.woocommerce?.current_revenue?.from_orders} recent orders
                                </Text>
                              )}
                            </Box>
                          </SimpleGrid>
                          
                          {/* Top Products */}
                          {integrationState[domain.domain]?.woocommerce?.top_products && 
                           integrationState[domain.domain]?.woocommerce?.top_products.length > 0 && (
                            <>
                              <Divider my={4} borderColor="green.200" />
                              <Box>
                                <Heading size="xs" mb={3} color="gray.600">Top Selling Products</Heading>
                                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={3}>
                                  {integrationState[domain.domain]?.woocommerce?.top_products?.slice(0, 3).map((product, index) => (
                                    <Box key={index} p={3} bg="white" borderRadius="md" border="1px" borderColor="green.200">
                                      <HStack spacing={3}>
                                        {product.image && (
                                          <Box
                                            w="40px"
                                            h="40px"
                                            bg="gray.100"
                                            borderRadius="md"
                                            backgroundImage={`url(${product.image})`}
                                            backgroundSize="cover"
                                            backgroundPosition="center"
                                          />
                                        )}
                                        <Box flex="1">
                                          <Text fontSize="sm" fontWeight="semibold" noOfLines={1}>
                                            {product.name}
                                          </Text>
                                          <Text fontSize="xs" color="gray.600">
                                            {product.total_sales} sales
                                          </Text>
                                          <Text fontSize="xs" fontWeight="bold">
                                            {integrationState[domain.domain]?.woocommerce?.store_info?.currency || 'ZAR'} {product.price}
                                          </Text>
                                        </Box>
                                      </HStack>
                                    </Box>
                                  )) || []}
                                </SimpleGrid>
                              </Box>
                            </>
                          )}
                          
                          <Divider my={4} borderColor="green.200" />
                          
                          <HStack justify="space-between" align="center">
                            <Box>
                              {integrationState[domain.domain]?.woocommerce?.last_updated && (
                                <Text fontSize="xs" color="gray.500">
                                  Last updated: {new Date(integrationState[domain.domain]?.woocommerce?.last_updated || '').toLocaleString()}
                                </Text>
                              )}
                            </Box>
                            <Button 
                              colorScheme="red" 
                              variant="outline" 
                              size="sm" 
                              onClick={() => handleDisconnect(domain.domain, 'woocommerce')}
                              isLoading={connectionLoading[domain.domain]}
                            >
                              Disconnect Store
                            </Button>
                          </HStack>
                        </Box>
                      ) : (
                        <>
                          <FormControl id={`${domain.domain}-woocommerce-url`}>
                            <FormLabel>Store URL</FormLabel>
                            <Input 
                              placeholder="shop.yourdomain.com" 
                              value={integrationState[domain.domain]?.woocommerce?.url || ''}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'url', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce?.connected}
                            />
                          </FormControl>
                          
                          <FormControl id={`${domain.domain}-woocommerce-key`}>
                            <FormLabel>Consumer Key</FormLabel>
                            <Input 
                              placeholder="ck_xxxxxxxxxxxxxxxxxxxx" 
                              value={integrationState[domain.domain]?.woocommerce?.key || ''}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'key', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce?.connected}
                            />
                          </FormControl>
                          
                          <FormControl id={`${domain.domain}-woocommerce-secret`}>
                            <FormLabel>Consumer Secret</FormLabel>
                            <Input 
                              placeholder="cs_xxxxxxxxxxxxxxxxxxxx" 
                              type="password"
                              value={integrationState[domain.domain]?.woocommerce?.secret || ''}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'secret', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce?.connected}
                            />
                          </FormControl>
                          
                          <Button 
                            colorScheme="teal"
                            isLoading={connectionLoading[domain.domain]}
                            onClick={() => handleConnect(domain.domain, 'woocommerce')}
                            isDisabled={
                              !integrationState[domain.domain]?.woocommerce?.url || 
                              !integrationState[domain.domain]?.woocommerce?.key || 
                              !integrationState[domain.domain]?.woocommerce?.secret
                            }
                          >
                            Connect WooCommerce
                          </Button>
                        </>
                      )}
                    </Stack>
                  </TabPanel>
                  
                  <TabPanel p={4} bg={panelBg} borderRadius="md" mt={4}>
                    <Stack spacing={4}>
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Heading size="sm" mb={1}>Google Analytics Integration</Heading>
                          <Text fontSize="sm" color={textColor}>
                            Connect Google Analytics to import visitors and traffic data.
                          </Text>
                        </Box>
                        <HStack>
                          {integrationState[domain.domain]?.googleAnalytics?.connected ? (
                            <Badge colorScheme="green" p={2} borderRadius="md">
                              Connected
                            </Badge>
                          ) : (
                            <Badge colorScheme="gray" p={2} borderRadius="md">
                              Not Connected
                            </Badge>
                          )}
                        </HStack>
                      </Flex>
                      
                      <Divider borderColor={borderColor} />
                      
                      <FormControl id={`${domain.domain}-ga-id`}>
                        <FormLabel>Measurement ID</FormLabel>
                        <Input 
                          placeholder="G-XXXXXXXXXX" 
                          value={integrationState[domain.domain]?.googleAnalytics?.measurementId || ''}
                          onChange={(e) => handleGoogleAnalyticsChange(domain.domain, 'measurementId', e.target.value)}
                          isDisabled={integrationState[domain.domain]?.googleAnalytics?.connected}
                        />
                      </FormControl>
                      
                      <FormControl id={`${domain.domain}-ga-secret`}>
                        <FormLabel>API Secret</FormLabel>
                        <Input 
                          placeholder="API Secret from Google Analytics" 
                          type="password"
                          value={integrationState[domain.domain]?.googleAnalytics?.apiSecret || ''}
                          onChange={(e) => handleGoogleAnalyticsChange(domain.domain, 'apiSecret', e.target.value)}
                          isDisabled={integrationState[domain.domain]?.googleAnalytics?.connected}
                        />
                      </FormControl>
                      
                      <Button 
                        colorScheme={integrationState[domain.domain]?.googleAnalytics?.connected ? "red" : "teal"}
                        onClick={() => integrationState[domain.domain]?.googleAnalytics?.connected 
                          ? handleDisconnect(domain.domain, 'googleAnalytics')
                          : handleConnect(domain.domain, 'googleAnalytics')
                        }
                        isDisabled={
                          !integrationState[domain.domain]?.googleAnalytics?.connected && 
                          (!integrationState[domain.domain]?.googleAnalytics?.measurementId || 
                           !integrationState[domain.domain]?.googleAnalytics?.apiSecret)
                        }
                      >
                        {integrationState[domain.domain]?.googleAnalytics?.connected ? "Disconnect" : "Connect"}
                      </Button>
                    </Stack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>
        ))
      )}
    </Box>
  );
} 