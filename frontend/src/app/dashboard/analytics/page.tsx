'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Select,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Flex,
  Text,
  Spinner,
  Grid,
  GridItem,
  HStack,
  Icon,
  Divider,
  Badge,
  useColorModeValue,
  Card,
  CardBody,
  CardHeader,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Image,
  VStack,
} from '@chakra-ui/react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { domainService, metricsService } from '@/services/api';
import { useChakraColor, CHART_COLOR } from '@/components/ui/theme-utils';

interface Domain {
  domain: string;
  name: string;
  woocommerce_enabled: boolean;
  ga_enabled: boolean;
}

interface Metric {
  domain: string;
  timestamp: number;
  pageviews: number;
  visitors: number;
  orders: number;
  revenue: number;
}

interface WooCommerceData {
  store_name: string;
  total_orders: number;
  current_revenue: number;
  currency: string;
  top_products: Array<{
    id: number;
    name: string;
    image: string;
    total_sales: number;
  }>;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  subtitle?: string;
  icon?: React.ReactElement;
}

function MetricCard({ title, value, change, subtitle, icon }: MetricCardProps) {
  const bgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const labelColor = useColorModeValue('gray.500', 'gray.400');
  const valueColor = useColorModeValue('gray.900', 'white');
  
  return (
    <Card
      px={4}
      py={4}
      bg={bgColor}
      borderColor={borderColor}
      borderWidth="1px"
      borderRadius="lg"
      shadow="sm"
      width="100%"
    >
      <CardHeader p={0} mb={2}>
        <Flex justifyContent="space-between" alignItems="center">
          <Text 
            fontWeight="medium" 
            color={labelColor} 
            fontSize="md"
          >
            {title}
          </Text>
          {icon && (
            <Box color="teal.200">
              {icon}
            </Box>
          )}
        </Flex>
      </CardHeader>
      <CardBody p={0}>
        <Flex alignItems="baseline">
          <Stat p={0}>
            <StatNumber fontSize="2xl" fontWeight="medium" color={valueColor}>
              {value}
            </StatNumber>
          </Stat>
          {change !== undefined && (
            <Badge 
              ml={2} 
              colorScheme={change >= 0 ? "green" : "red"} 
              borderRadius="full"
              px={2}
              py={0.5}
            >
              <Flex alignItems="center">
                <Stat display="inline" p={0} m={0}>
                  <StatArrow type={change >= 0 ? "increase" : "decrease"} />
                </Stat>
                {Math.abs(change)}%
              </Flex>
            </Badge>
          )}
        </Flex>
        {subtitle && (
          <Text fontSize="sm" color={labelColor} mt={1}>
            {subtitle}
          </Text>
        )}
      </CardBody>
    </Card>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  const bgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headingColor = useColorModeValue('gray.700', 'white');
  
  return (
    <Card
      bg={bgColor}
      borderColor={borderColor}
      borderWidth="1px"
      borderRadius="lg"
      shadow="sm"
      width="100%"
      overflow="hidden"
    >
      <CardHeader py={3} px={4}>
        <Heading size="sm" color={headingColor}>
          {title}
        </Heading>
      </CardHeader>
      <Divider borderColor={borderColor} />
      <CardBody p={4}>
        {children}
      </CardBody>
    </Card>
  );
}

function SectionHeading({ title, subtitle }: { title: string; subtitle?: string }) {
  const headingColor = useColorModeValue('gray.700', 'white');
  
  return (
    <Flex direction="column" mb={4}>
      <Flex alignItems="center" mb={1}>
        <Heading size="md" color={headingColor}>{title}</Heading>
        {subtitle && (
          <Badge ml={2} colorScheme="blue" variant="subtle">
            {subtitle}
          </Badge>
        )}
      </Flex>
      <Divider borderColor={useColorModeValue('gray.200', 'gray.700')} />
    </Flex>
  );
}

export default function AnalyticsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [wooCommerceData, setWooCommerceData] = useState<WooCommerceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [wooCommerceLoading, setWooCommerceLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  const headingColor = useColorModeValue('gray.700', 'white');
  const selectBg = useColorModeValue('white', '#171923');
  const selectBorderColor = useColorModeValue('gray.200', 'gray.600');
  const tabBg = useColorModeValue('gray.50', 'gray.800');
  const tealColor = CHART_COLOR; // Use the constant directly

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const { domains } = await domainService.getDomains();
        setDomains(domains);
        if (domains.length > 0) {
          setSelectedDomain(domains[0].domain);
        }
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch domains');
      } finally {
        setLoading(false);
      }
    };

    fetchDomains();
  }, []);

  useEffect(() => {
    const fetchMetrics = async () => {
      if (!selectedDomain) return;

      try {
        const { metrics } = await metricsService.getMetrics(selectedDomain);
        setMetrics(metrics);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch metrics');
      }
    };

    fetchMetrics();
  }, [selectedDomain]);

  useEffect(() => {
    const fetchWooCommerceData = async () => {
      if (!selectedDomain) return;

      // Check if the selected domain has WooCommerce enabled
      const domain = domains.find(d => d.domain === selectedDomain);
      if (!domain?.woocommerce_enabled) {
        setWooCommerceData(null);
        return;
      }

      try {
        setWooCommerceLoading(true);
        const data = await domainService.getIntegrationDetails(selectedDomain, 'woocommerce');
        setWooCommerceData(data);
      } catch (err: any) {
        console.error('Failed to fetch WooCommerce data:', err);
        // Only set to null if it's a real error, not a timeout
        if (err.message?.includes('timeout') || err.message?.includes('Network error')) {
          console.log('WooCommerce data fetch timed out, retrying...');
          // Don't set to null, keep the loading state for retry
        } else {
          setWooCommerceData(null);
        }
      } finally {
        setWooCommerceLoading(false);
      }
    };

    if (domains.length > 0) {
      fetchWooCommerceData();
    }
  }, [selectedDomain, domains]);

  // Calculate trends
  const calculateTrend = (metricName: keyof Metric) => {
    if (metrics.length < 2) return { value: 0, isIncrease: true };
    
    const current = metrics[metrics.length - 1][metricName] as number;
    const previous = metrics[metrics.length - 2][metricName] as number;
    
    const percentChange = ((current - previous) / previous) * 100;
    return {
      value: Math.abs(percentChange).toFixed(1),
      isIncrease: percentChange >= 0
    };
  };

  // Format data for charts
  const chartData = metrics.map(metric => ({
    ...metric,
    date: new Date(metric.timestamp * 1000).toLocaleDateString(),
    conversionRate: ((metric.orders / metric.visitors) * 100).toFixed(2)
  })).reverse();

  // Traffic source data for pie chart
  const trafficSources = [
    { name: 'Organic', value: 40 },
    { name: 'Direct', value: 30 },
    { name: 'Referral', value: 20 },
    { name: 'Social', value: 10 },
  ];
  
  const COLORS = [CHART_COLOR, 'rgba(129, 230, 217, 0.8)', 'rgba(129, 230, 217, 0.6)', 'rgba(129, 230, 217, 0.4)'];
  
  // Visitor conversion data
  const getConversionData = () => {
    if (metrics.length === 0) return [];
    const latest = metrics[metrics.length - 1];
    return [
      { name: 'Converted', value: latest.orders },
      { name: 'Non-Converted', value: latest.visitors - latest.orders }
    ];
  };

  const conversionData = getConversionData();
  const CONVERSION_COLORS = [CHART_COLOR, 'rgba(129, 230, 217, 0.3)'];

  if (loading) {
    return (
      <Flex height="calc(100vh - 80px)" align="center" justify="center">
        <Spinner size="xl" color="teal.200" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box p={4} bg="red.50" color="red.500" borderRadius="md">
        {error}
      </Box>
    );
  }

  return (
    <Box maxW="1400px" mx="auto" py={5} px={{ base: 2, sm: 4, md: 6 }}>
      <Flex mb={6} justifyContent="space-between" alignItems="center">
        <Heading size="lg" mb={0} color={headingColor}>
          Analytics
        </Heading>
        <FormControl id="domain-select-analytics-form" maxW="300px">
          <FormLabel htmlFor="domain-select-analytics">Select Domain</FormLabel>
          <Select
            id="domain-select-analytics"
            name="domain-select-analytics"
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            bg={selectBg}
            borderColor={selectBorderColor}
            aria-label="Select a domain to view analytics"
          >
            {domains.map((domain) => (
              <option key={domain.domain} value={domain.domain}>
                {domain.name} ({domain.domain})
              </option>
            ))}
          </Select>
        </FormControl>
      </Flex>

      {metrics.length > 0 && (
        <>
          <SectionHeading 
            title="Performance Metrics" 
            subtitle={`Last Updated: ${new Date().toLocaleDateString()}`} 
          />
          
          <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={5} mb={8}>
            <MetricCard
              title="Total Revenue"
              value={`$${metrics[0].revenue.toFixed(2)}`}
              change={Number(calculateTrend('revenue').value) * (calculateTrend('revenue').isIncrease ? 1 : -1)}
              subtitle="This month"
            />
            <MetricCard
              title="Orders"
              value={metrics[0].orders}
              change={Number(calculateTrend('orders').value) * (calculateTrend('orders').isIncrease ? 1 : -1)}
              subtitle="vs last month"
            />
            <MetricCard
              title="Page Views"
              value={metrics[0].pageviews.toLocaleString()}
              change={Number(calculateTrend('pageviews').value) * (calculateTrend('pageviews').isIncrease ? 1 : -1)}
              subtitle="Total visits"
            />
            <MetricCard
              title="Visitors"
              value={metrics[0].visitors.toLocaleString()}
              change={Number(calculateTrend('visitors').value) * (calculateTrend('visitors').isIncrease ? 1 : -1)}
              subtitle="Unique visitors"
            />
          </SimpleGrid>

          {/* WooCommerce Data Section */}
          {domains.find(d => d.domain === selectedDomain)?.woocommerce_enabled && (
            <>
              <SectionHeading 
                title="WooCommerce Data" 
                subtitle={domains.find(d => d.domain === selectedDomain)?.name?.toUpperCase() || selectedDomain.toUpperCase()}
              />
              
              {wooCommerceLoading ? (
                <Flex justify="center" py={8}>
                  <Spinner size="lg" color="teal.200" />
                </Flex>
              ) : wooCommerceData ? (
                <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6} mb={8}>
                  <GridItem>
                    <Card
                      bg={useColorModeValue('white', '#171923')}
                      borderColor={useColorModeValue('gray.200', 'gray.700')}
                      borderWidth="1px"
                      borderRadius="lg"
                      shadow="sm"
                    >
                      <CardHeader>
                        <Heading size="md" color={headingColor}>Store Overview</Heading>
                      </CardHeader>
                      <CardBody>
                        <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={6}>
                          <MetricCard
                            title="Today's Revenue"
                            value={`${wooCommerceData.currency} 0.00`}
                            subtitle="Last 24 hours"
                          />
                          <MetricCard
                            title="Weekly Revenue"
                            value={`${wooCommerceData.currency} 0.00`}
                            subtitle="Last 7 days"
                          />
                          <MetricCard
                            title="Today's Orders"
                            value="0"
                            subtitle="Last 24 hours"
                          />
                          <MetricCard
                            title="Total Products"
                            value="0"
                            subtitle="Total products"
                          />
                        </SimpleGrid>
                        
                        <Divider my={6} borderColor={useColorModeValue('gray.200', 'gray.700')} />
                        
                        <VStack align="stretch" spacing={4}>
                          <Flex justify="space-between" align="center">
                            <Text fontSize="lg" fontWeight="semibold" color={headingColor}>
                              Store Performance
                            </Text>
                            <Badge colorScheme="green" px={3} py={1} borderRadius="full">
                              Connected
                            </Badge>
                          </Flex>
                          
                          <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={4}>
                            <Box>
                              <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')} mb={1}>
                                Total Orders
                              </Text>
                              <Text fontSize="2xl" fontWeight="bold" color="teal.200">
                                {wooCommerceData.total_orders}
                              </Text>
                            </Box>
                            <Box>
                              <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')} mb={1}>
                                Total Revenue
                              </Text>
                              <Text fontSize="2xl" fontWeight="bold" color="teal.200">
                                {wooCommerceData.currency} {wooCommerceData.current_revenue.toFixed(2)}
                              </Text>
                              <Text fontSize="xs" color={useColorModeValue('gray.500', 'gray.500')}>
                                From {wooCommerceData.total_orders} recent orders
                              </Text>
                            </Box>
                          </SimpleGrid>
                        </VStack>
                      </CardBody>
                    </Card>
                  </GridItem>
                  
                  <GridItem>
                    <Card
                      bg={useColorModeValue('white', '#171923')}
                      borderColor={useColorModeValue('gray.200', 'gray.700')}
                      borderWidth="1px"
                      borderRadius="lg"
                      shadow="sm"
                    >
                      <CardHeader>
                        <Heading size="md" color={headingColor}>Top Selling Products</Heading>
                      </CardHeader>
                      <CardBody>
                        {wooCommerceData.top_products && wooCommerceData.top_products.length > 0 ? (
                          <VStack spacing={4} align="stretch">
                            {wooCommerceData.top_products.slice(0, 3).map((product, index) => (
                              <Flex key={product.id} align="center" p={3} bg={useColorModeValue('gray.50', 'gray.800')} borderRadius="md">
                                <Box mr={3} position="relative">
                                  <Badge
                                    position="absolute"
                                    top="-8px"
                                    left="-8px"
                                    colorScheme="teal"
                                    borderRadius="full"
                                    fontSize="xs"
                                    minW="20px"
                                    h="20px"
                                    display="flex"
                                    alignItems="center"
                                    justifyContent="center"
                                  >
                                    {index + 1}
                                  </Badge>
                                  <Image
                                    src={product.image || '/placeholder-product.png'}
                                    alt={product.name}
                                    boxSize="50px"
                                    objectFit="cover"
                                    borderRadius="md"
                                    fallbackSrc="/placeholder-product.png"
                                  />
                                </Box>
                                <Box flex="1">
                                  <Text fontSize="sm" fontWeight="medium" color={headingColor} noOfLines={2}>
                                    {product.name}
                                  </Text>
                                  <Text fontSize="xs" color="teal.200" fontWeight="semibold">
                                    {product.total_sales} sales
                                  </Text>
                                </Box>
                              </Flex>
                            ))}
                          </VStack>
                        ) : (
                          <Text color={useColorModeValue('gray.500', 'gray.400')} textAlign="center" py={4}>
                            No product data available
                          </Text>
                        )}
                      </CardBody>
                    </Card>
                  </GridItem>
                </Grid>
              ) : (
                <Card
                  bg={useColorModeValue('gray.50', 'gray.800')}
                  borderColor={useColorModeValue('gray.200', 'gray.700')}
                  borderWidth="1px"
                  borderRadius="lg"
                  p={6}
                  mb={8}
                >
                  <VStack spacing={3}>
                    <Text color={useColorModeValue('gray.600', 'gray.400')} textAlign="center">
                      WooCommerce integration is enabled but no data is available.
                    </Text>
                    <Text fontSize="sm" color={useColorModeValue('gray.500', 'gray.500')} textAlign="center">
                      Please check your WooCommerce connection in the Integrations page.
                    </Text>
                  </VStack>
                </Card>
              )}
            </>
          )}
          
          <Tabs 
            variant="enclosed" 
            colorScheme="teal" 
            mb={8}
            onChange={(index) => setActiveTab(index)}
          >
            <TabList>
              <Tab>Traffic & Revenue</Tab>
              <Tab>Conversions</Tab>
            </TabList>
            <TabPanels>
              <TabPanel p={0} pt={6}>
                <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6} mb={8}>
                  <GridItem colSpan={{ base: 1, lg: 2 }}>
                    <ChartCard title="Revenue Over Time">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart
                            data={chartData}
                            margin={{
                              top: 10,
                              right: 30,
                              left: 0,
                              bottom: 0,
                            }}
                          >
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <RechartsTooltip />
                            <Area
                              type="monotone"
                              dataKey="revenue"
                              stroke={CHART_COLOR}
                              fill="rgba(129, 230, 217, 0.2)"
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                  
                  <GridItem>
                    <ChartCard title="Visitors & Pageviews">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={chartData}
                            margin={{
                              top: 10,
                              right: 30,
                              left: 0,
                              bottom: 0,
                            }}
                          >
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <RechartsTooltip />
                            <Legend />
                            <Line 
                              type="monotone" 
                              dataKey="visitors" 
                              stroke={CHART_COLOR} 
                              strokeWidth={2}
                              activeDot={{ r: 8 }}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="pageviews" 
                              stroke={CHART_COLOR} 
                              strokeWidth={2}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                  
                  <GridItem>
                    <ChartCard title="Traffic Sources">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={trafficSources}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={90}
                              paddingAngle={5}
                              dataKey="value"
                              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            >
                              {trafficSources.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Pie>
                            <RechartsTooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                </Grid>
              </TabPanel>
              
              <TabPanel p={0} pt={6}>
                <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6} mb={8}>
                  <GridItem>
                    <ChartCard title="Conversion Rate Over Time">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={chartData}
                            margin={{
                              top: 10,
                              right: 30,
                              left: 0,
                              bottom: 0,
                            }}
                          >
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <RechartsTooltip />
                            <Line 
                              type="monotone" 
                              dataKey="conversionRate" 
                              name="Conversion Rate (%)"
                              stroke={CHART_COLOR} 
                              strokeWidth={2}
                              activeDot={{ r: 8 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                  
                  <GridItem>
                    <ChartCard title="Visitor Conversion">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={conversionData}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={90}
                              paddingAngle={5}
                              dataKey="value"
                              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                            >
                              {conversionData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={CONVERSION_COLORS[index % CONVERSION_COLORS.length]} />
                              ))}
                            </Pie>
                            <RechartsTooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                  
                  <GridItem colSpan={{ base: 1, lg: 2 }}>
                    <ChartCard title="Orders & Revenue Comparison">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={chartData}
                            margin={{
                              top: 10,
                              right: 30,
                              left: 0,
                              bottom: 0,
                            }}
                          >
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="date" />
                            <YAxis yAxisId="left" orientation="left" />
                            <YAxis yAxisId="right" orientation="right" />
                            <RechartsTooltip />
                            <Legend />
                            <Bar 
                              yAxisId="left" 
                              dataKey="orders" 
                              name="Orders" 
                              fill={CHART_COLOR} 
                            />
                            <Bar 
                              yAxisId="right" 
                              dataKey="revenue" 
                              name="Revenue ($)" 
                              fill={CHART_COLOR} 
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </Box>
                    </ChartCard>
                  </GridItem>
                </Grid>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </>
      )}
    </Box>
  );
} 