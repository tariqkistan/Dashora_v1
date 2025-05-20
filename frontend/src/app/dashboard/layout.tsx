'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Text,
  Heading,
  Button,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  VStack,
  HStack,
  IconButton,
  useDisclosure,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Icon,
  Divider,
  useColorModeValue,
  Spinner,
  Center,
  Avatar,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverBody,
  PopoverArrow,
  PopoverCloseButton,
  Badge,
} from '@chakra-ui/react';
import { useRouter } from 'next/navigation';
import { deleteCookie } from 'cookies-next';
import { ColorModeButton } from '@/components/ui/color-mode';
import React from 'react';
import { navigation } from './navigation';

const notifications = [
  { id: 1, title: 'New order received', time: '5 minutes ago', read: false },
  { id: 2, title: 'Your analytics report is ready', time: '2 hours ago', read: false },
  { id: 3, title: 'Welcome to Dashora', time: '1 day ago', read: true },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  // Colors
  const bgColor = useColorModeValue('white', '#171923');
  const sidebarBgColor = useColorModeValue('white', '#171923');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const accentColor = useColorModeValue('brand.500', 'teal.200');
  const textColor = useColorModeValue('gray.700', 'gray.50');
  const navHoverBg = useColorModeValue('gray.50', 'gray.800');

  // Only render UI after hydration to avoid mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = () => {
    deleteCookie('auth_token');
    router.push('/login');
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
    <Box>
      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent bg={sidebarBgColor} maxW="56">
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px" borderColor={borderColor} py={3}>
            <Heading size="md" color={accentColor}>Dashora</Heading>
          </DrawerHeader>
          <DrawerBody p={0}>
            <VStack align="stretch" spacing={0}>
              {navigation.map((item) => (
                <Button
                  key={item.name}
                  as="a"
                  href={item.href}
                  variant="ghost"
                  justifyContent="flex-start"
                  leftIcon={
                    <Box>
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="20" height="20">
                        <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                      </svg>
                    </Box>
                  }
                  py={2}
                  px={3}
                  fontSize="sm"
                  fontWeight="semibold"
                  _hover={{ bg: navHoverBg, color: accentColor }}
                >
                  {item.name}
                </Button>
              ))}
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Desktop Sidebar */}
      <Box
        display={{ base: 'none', lg: 'block' }}
        position="fixed"
        left={0}
        top={0}
        h="100vh"
        w="56"
        bg={sidebarBgColor}
        borderRightWidth="1px"
        borderColor={borderColor}
        overflowY="auto"
        zIndex={30}
      >
        <Box p={4}>
          <Heading size="md" color={accentColor} py={3}>Dashora</Heading>
          <VStack align="stretch" spacing={1} mt={4}>
            {navigation.map((item) => (
              <Button
                key={item.name}
                as="a"
                href={item.href}
                variant="ghost"
                justifyContent="flex-start"
                leftIcon={
                  <Box>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="20" height="20">
                      <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                    </svg>
                  </Box>
                }
                py={2}
                px={3}
                rounded="md"
                fontSize="sm"
                fontWeight="semibold"
                _hover={{ bg: navHoverBg, color: accentColor }}
              >
                {item.name}
              </Button>
            ))}
          </VStack>
        </Box>
      </Box>

      {/* Main Content */}
      <Box ml={{ base: 0, lg: '56' }}>
        {/* Top Header */}
        <Flex
          as="header"
          position="sticky"
          top={0}
          zIndex={10}
          h="16"
          bg={bgColor}
          borderBottomWidth="1px"
          borderColor={borderColor}
          px={{ base: 4, md: 6, lg: 8 }}
          alignItems="center"
          boxShadow="sm"
        >
          {/* Mobile menu button */}
          <IconButton
            display={{ base: 'flex', lg: 'none' }}
            onClick={onOpen}
            aria-label="Open menu"
            variant="ghost"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="24" height="24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            }
          />

          <Box flex={1} />

          {/* Notification Center */}
          <Popover placement="bottom-end">
            <PopoverTrigger>
              <Box position="relative" mr={4}>
                <IconButton
                  aria-label="Notifications"
                  variant="ghost"
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="24" height="24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
                    </svg>
                  }
                />
                {notifications.filter(n => !n.read).length > 0 && (
                  <Badge 
                    position="absolute" 
                    top="-5px" 
                    right="-5px" 
                    colorScheme="red" 
                    borderRadius="full" 
                    fontSize="xs"
                  >
                    {notifications.filter(n => !n.read).length}
                  </Badge>
                )}
              </Box>
            </PopoverTrigger>
            <PopoverContent
              bg={bgColor}
              borderColor={borderColor}
              width="300px"
              _focus={{ boxShadow: 'none' }}
            >
              <PopoverArrow bg={bgColor} />
              <PopoverHeader borderColor={borderColor} fontWeight="semibold">
                Notifications
              </PopoverHeader>
              <PopoverBody p={0}>
                <VStack align="stretch" spacing={0} maxH="320px" overflow="auto">
                  {notifications.length === 0 ? (
                    <Box py={4} textAlign="center" color={textColor}>
                      No new notifications
                    </Box>
                  ) : (
                    notifications.map(notification => (
                      <Flex
                        key={notification.id}
                        p={3}
                        borderBottomWidth="1px"
                        borderColor={borderColor}
                        bg={notification.read ? 'transparent' : 'rgba(129, 230, 217, 0.1)'}
                        _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                        cursor="pointer"
                      >
                        <Box mr={3} color="teal.200">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="20" height="20">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 9.75a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 0 1 .778-.332 48.294 48.294 0 0 0 5.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
                          </svg>
                        </Box>
                        <Box flex={1}>
                          <Text fontSize="sm" fontWeight={notification.read ? 'normal' : 'semibold'}>
                            {notification.title}
                          </Text>
                          <Text fontSize="xs" color={textColor}>
                            {notification.time}
                          </Text>
                        </Box>
                      </Flex>
                    ))
                  )}
                </VStack>
                <Box p={2} borderTopWidth="1px" borderColor={borderColor}>
                  <Text 
                    fontSize="sm" 
                    textAlign="center" 
                    color="teal.200" 
                    fontWeight="medium" 
                    cursor="pointer"
                    _hover={{ textDecoration: 'underline' }}
                  >
                    Mark all as read
                  </Text>
                </Box>
              </PopoverBody>
            </PopoverContent>
          </Popover>

          {/* Color Mode Toggle */}
          <ColorModeButton />
          
          {/* User menu */}
          <Menu>
            <MenuButton as={Button} variant="ghost" px={2} ml={2}>
              <HStack spacing={2}>
                <Avatar 
                  size="sm" 
                  name="Admin User" 
                  bg="teal.400" 
                  color="white"
                  src="https://bit.ly/broken-link" 
                />
                <Text fontWeight="semibold" display={{ base: 'none', md: 'block' }}>Admin User</Text>
              </HStack>
            </MenuButton>
            <MenuList bg={bgColor} borderColor={borderColor}>
              <MenuItem _hover={{ bg: navHoverBg }}>Profile</MenuItem>
              <MenuItem _hover={{ bg: navHoverBg }}>Settings</MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout} _hover={{ bg: navHoverBg }}>Sign out</MenuItem>
            </MenuList>
          </Menu>
        </Flex>

        {/* Main content area */}
        <Box as="main" py={10} px={{ base: 4, md: 6, lg: 8 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
} 