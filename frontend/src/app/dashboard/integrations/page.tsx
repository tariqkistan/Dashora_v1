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
} from '@chakra-ui/react';
import { domainService } from '@/services/api';

interface Domain {
  domain: string;
  name: string;
  woocommerce_enabled: boolean;
  ga_enabled: boolean;
}

interface IntegrationState {
  [key: string]: {
    woocommerce: {
      url: string;
      key: string;
      secret: string;
      connected: boolean;
    };
    googleAnalytics: {
      measurementId: string;
      apiSecret: string;
      connected: boolean;
    };
  };
}

export default function IntegrationsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [integrationState, setIntegrationState] = useState<IntegrationState>({});
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.700', 'white');
  const panelBg = useColorModeValue('gray.50', 'gray.800');
  
  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const { domains } = await domainService.getDomains();
        setDomains(domains);
        
        // Initialize state with existing integration data from domains
        const initialState: IntegrationState = {};
        domains.forEach(domain => {
          initialState[domain.domain] = {
            woocommerce: {
              url: '',
              key: '',
              secret: '',
              connected: domain.woocommerce_enabled
            },
            googleAnalytics: {
              measurementId: '',
              apiSecret: '',
              connected: domain.ga_enabled
            }
          };
        });
        
        setIntegrationState(initialState);
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
  
  const handleConnect = (domain: string, integrationType: 'woocommerce' | 'googleAnalytics') => {
    const integration = integrationState[domain][integrationType];
    
    // In a real application, you would make an API call to connect the integration
    // For this example, we'll just simulate success
    
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
      title: `${integrationType === 'woocommerce' ? 'WooCommerce' : 'Google Analytics'} Connected`,
      description: `Successfully connected ${domain} to ${integrationType === 'woocommerce' ? 'WooCommerce' : 'Google Analytics'}`,
      status: 'success',
      duration: 5000,
      isClosable: true,
    });
  };
  
  const handleDisconnect = (domain: string, integrationType: 'woocommerce' | 'googleAnalytics') => {
    // In a real application, you would make an API call to disconnect the integration
    
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
      title: `${integrationType === 'woocommerce' ? 'WooCommerce' : 'Google Analytics'} Disconnected`,
      description: `Successfully disconnected ${domain} from ${integrationType === 'woocommerce' ? 'WooCommerce' : 'Google Analytics'}`,
      status: 'info',
      duration: 5000,
      isClosable: true,
    });
  };

  return (
    <Box maxW="1400px" mx="auto" py={5} px={{ base: 2, sm: 4, md: 6 }}>
      <Heading size="lg" mb={6} color={headingColor}>
        Integrations
      </Heading>
      
      <Text mb={8} color={textColor}>
        Connect your domains to WooCommerce and Google Analytics to enable data synchronization and comprehensive analytics.
      </Text>
      
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
                      
                      <FormControl id={`${domain.domain}-woocommerce-url`}>
                        <FormLabel>Store URL</FormLabel>
                        <Input 
                          placeholder="https://yourdomain.com" 
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
                        colorScheme={integrationState[domain.domain]?.woocommerce.connected ? "red" : "teal"}
                        onClick={() => integrationState[domain.domain]?.woocommerce.connected 
                          ? handleDisconnect(domain.domain, 'woocommerce')
                          : handleConnect(domain.domain, 'woocommerce')
                        }
                        isDisabled={
                          !integrationState[domain.domain]?.woocommerce.connected && 
                          (!integrationState[domain.domain]?.woocommerce.url || 
                           !integrationState[domain.domain]?.woocommerce.key || 
                           !integrationState[domain.domain]?.woocommerce.secret)
                        }
                      >
                        {integrationState[domain.domain]?.woocommerce.connected ? "Disconnect" : "Connect"}
                      </Button>
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