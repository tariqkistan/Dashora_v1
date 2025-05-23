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
} from '@chakra-ui/react';
import { domainService } from '@/services/api';

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
  product_count?: number;
  last_order_date?: string;
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

export default function IntegrationsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectionLoading, setConnectionLoading] = useState<{[key: string]: boolean}>({});
  const [error, setError] = useState('');
  const [integrationState, setIntegrationState] = useState<IntegrationState>({});
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.700', 'white');
  const panelBg = useColorModeValue('gray.50', 'gray.800');
  const successBg = useColorModeValue('green.50', 'green.900');
  
  useEffect(() => {
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
        domains.forEach(async (domain: Domain) => {
          if (domain.woocommerce_enabled) {
            try {
              // Get connection details if WooCommerce is already enabled
              const details = await domainService.getIntegrationDetails(domain.domain, 'woocommerce');
              
              if (details) {
                setIntegrationState(prev => ({
                  ...prev,
                  [domain.domain]: {
                    ...prev[domain.domain],
                    woocommerce: {
                      ...prev[domain.domain].woocommerce,
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
        });
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch domains');
      } finally {
        setLoading(false);
      }
    };

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
      <Heading size="lg" mb={6} color={headingColor}>
        Integrations
      </Heading>
      
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
                          
                          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                            <Box>
                              <Text fontWeight="bold" fontSize="sm">Store Name</Text>
                              <Text>{integrationState[domain.domain]?.woocommerce.store_name || domain.name}</Text>
                            </Box>
                            
                            {integrationState[domain.domain]?.woocommerce.product_count !== undefined && (
                              <Box>
                                <Text fontWeight="bold" fontSize="sm">Products</Text>
                                <Text>{integrationState[domain.domain]?.woocommerce.product_count}</Text>
                              </Box>
                            )}
                            
                            {integrationState[domain.domain]?.woocommerce.last_order_date && (
                              <Box>
                                <Text fontWeight="bold" fontSize="sm">Last Order</Text>
                                <Text>{new Date(integrationState[domain.domain]?.woocommerce.last_order_date || '').toLocaleDateString()}</Text>
                              </Box>
                            )}
                          </SimpleGrid>
                          
                          <Divider my={4} borderColor="green.200" />
                          
                          <Button 
                            colorScheme="red" 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleDisconnect(domain.domain, 'woocommerce')}
                            isLoading={connectionLoading[domain.domain]}
                          >
                            Disconnect Store
                          </Button>
                        </Box>
                      ) : (
                        <>
                          <FormControl id={`${domain.domain}-woocommerce-url`}>
                            <FormLabel>Store URL</FormLabel>
                            <Input 
                              placeholder="shop.yourdomain.com" 
                              value={integrationState[domain.domain]?.woocommerce.url}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'url', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce.connected}
                            />
                          </FormControl>
                          
                          <FormControl id={`${domain.domain}-woocommerce-key`}>
                            <FormLabel>Consumer Key</FormLabel>
                            <Input 
                              placeholder="ck_xxxxxxxxxxxxxxxxxxxx" 
                              value={integrationState[domain.domain]?.woocommerce.key}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'key', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce.connected}
                            />
                          </FormControl>
                          
                          <FormControl id={`${domain.domain}-woocommerce-secret`}>
                            <FormLabel>Consumer Secret</FormLabel>
                            <Input 
                              placeholder="cs_xxxxxxxxxxxxxxxxxxxx" 
                              type="password"
                              value={integrationState[domain.domain]?.woocommerce.secret}
                              onChange={(e) => handleWooCommerceChange(domain.domain, 'secret', e.target.value)}
                              isDisabled={integrationState[domain.domain]?.woocommerce.connected}
                            />
                          </FormControl>
                          
                          <Button 
                            colorScheme="teal"
                            isLoading={connectionLoading[domain.domain]}
                            onClick={() => handleConnect(domain.domain, 'woocommerce')}
                            isDisabled={
                              !integrationState[domain.domain]?.woocommerce.url || 
                              !integrationState[domain.domain]?.woocommerce.key || 
                              !integrationState[domain.domain]?.woocommerce.secret
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
                          {integrationState[domain.domain]?.googleAnalytics.connected ? (
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
                          value={integrationState[domain.domain]?.googleAnalytics.measurementId}
                          onChange={(e) => handleGoogleAnalyticsChange(domain.domain, 'measurementId', e.target.value)}
                          isDisabled={integrationState[domain.domain]?.googleAnalytics.connected}
                        />
                      </FormControl>
                      
                      <FormControl id={`${domain.domain}-ga-secret`}>
                        <FormLabel>API Secret</FormLabel>
                        <Input 
                          placeholder="API Secret from Google Analytics" 
                          type="password"
                          value={integrationState[domain.domain]?.googleAnalytics.apiSecret}
                          onChange={(e) => handleGoogleAnalyticsChange(domain.domain, 'apiSecret', e.target.value)}
                          isDisabled={integrationState[domain.domain]?.googleAnalytics.connected}
                        />
                      </FormControl>
                      
                      <Button 
                        colorScheme={integrationState[domain.domain]?.googleAnalytics.connected ? "red" : "teal"}
                        onClick={() => integrationState[domain.domain]?.googleAnalytics.connected 
                          ? handleDisconnect(domain.domain, 'googleAnalytics')
                          : handleConnect(domain.domain, 'googleAnalytics')
                        }
                        isDisabled={
                          !integrationState[domain.domain]?.googleAnalytics.connected && 
                          (!integrationState[domain.domain]?.googleAnalytics.measurementId || 
                           !integrationState[domain.domain]?.googleAnalytics.apiSecret)
                        }
                      >
                        {integrationState[domain.domain]?.googleAnalytics.connected ? "Disconnect" : "Connect"}
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