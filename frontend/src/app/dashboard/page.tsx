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

export default function DashboardPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  const headingColor = useColorModeValue('gray.700', 'white');
  const selectBg = useColorModeValue('white', '#171923');
  const selectBorderColor = useColorModeValue('gray.200', 'gray.600');
  const tabBg = useColorModeValue('gray.50', 'gray.800');
  const tealColor = CHART_COLOR;
  
  // Sample keyword data for demo
  const keywordData = [
    { keyword: 'analytics dashboard', position: 1, change: 0 },
    { keyword: 'multi-site analytics', position: 3, change: 2 },
    { keyword: 'e-commerce dashboard', position: 5, change: -1 },
    { keyword: 'site performance', position: 8, change: 3 },
    { keyword: 'conversion metrics', position: 10, change: 0 },
  ];
  
  // Generate fake traffic source data
  const trafficSources = [
    { name: 'Organic', value: 40 },
    { name: 'Direct', value: 30 },
    { name: 'Referral', value: 20 },
    { name: 'Social', value: 10 },
  ];
  
  const COLORS = [CHART_COLOR, 'rgba(129, 230, 217, 0.8)', 'rgba(129, 230, 217, 0.6)', 'rgba(129, 230, 217, 0.4)'];

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
          Dashboard
        </Heading>
        <FormControl id="domain-select-form" maxW="300px">
          <FormLabel htmlFor="domain-select">Select Domain</FormLabel>
          <Select
            id="domain-select"
            name="domain-select"
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            bg={selectBg}
            borderColor={selectBorderColor}
            aria-label="Select a domain to view its analytics"
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
              change={3.2}
              subtitle="This month"
            />
            <MetricCard
              title="Orders"
              value={metrics[0].orders}
              change={-1.5}
              subtitle="vs last month"
            />
            <MetricCard
              title="Page Views"
              value={metrics[0].pageviews.toLocaleString()}
              change={15.1}
              subtitle="Total visits"
            />
            <MetricCard
              title="Visitors"
              value={metrics[0].visitors.toLocaleString()}
              change={8.4}
              subtitle="Unique visitors"
            />
          </SimpleGrid>
          
          <Tabs 
            variant="enclosed" 
            colorScheme="teal" 
            mb={8}
            onChange={(index) => setActiveTab(index)}
          >
            <TabList>
              <Tab>Traffic & Revenue</Tab>
              <Tab>Keyword Rankings</Tab>
            </TabList>
            <TabPanels>
              <TabPanel p={0} pt={6}>
                <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6} mb={8}>
                  <GridItem>
                    <ChartCard title="Revenue Trend">
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart
                            data={metrics.slice().reverse()}
                            margin={{
                              top: 10,
                              right: 30,
                              left: 0,
                              bottom: 0,
                            }}
                          >
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis
                              dataKey="timestamp"
                              tickFormatter={(timestamp) =>
                                new Date(timestamp * 1000).toLocaleDateString()
                              }
                            />
                            <YAxis />
                            <RechartsTooltip
                              labelFormatter={(timestamp) =>
                                new Date(timestamp * 1000).toLocaleDateString()
                              }
                            />
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
                <ChartCard title="Top Keywords Performance">
                  <Box overflowX="auto">
                    <Flex direction="column" width="100%">
                      <Flex 
                        py={2} 
                        borderBottomWidth="1px" 
                        borderColor={useColorModeValue('gray.200', 'gray.700')}
                        fontWeight="bold"
                      >
                        <Box width="50%">Keyword</Box>
                        <Box width="25%" textAlign="center">Position</Box>
                        <Box width="25%" textAlign="center">Change</Box>
                      </Flex>
                      {keywordData.map((item, index) => (
                        <Flex 
                          key={index} 
                          py={3} 
                          borderBottomWidth="1px" 
                          borderColor={useColorModeValue('gray.100', 'gray.800')}
                          _hover={{ bg: useColorModeValue('gray.50', 'gray.900') }}
                        >
                          <Box width="50%">{item.keyword}</Box>
                          <Box width="25%" textAlign="center">{item.position}</Box>
                          <Box width="25%" textAlign="center">
                            <Badge 
                              colorScheme={item.change > 0 ? "green" : item.change < 0 ? "red" : "gray"}
                              borderRadius="full"
                              px={2}
                              py={0.5}
                            >
                              <Flex alignItems="center">
                                {item.change !== 0 && (
                                  <Stat display="inline" p={0} m={0}>
                                    <StatArrow type={item.change > 0 ? "increase" : "decrease"} />
                                  </Stat>
                                )}
                                {item.change === 0 ? '–' : Math.abs(item.change)}
                              </Flex>
                            </Badge>
                          </Box>
                        </Flex>
                      ))}
                    </Flex>
                  </Box>
                </ChartCard>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </>
      )}
    </Box>
  );
} 