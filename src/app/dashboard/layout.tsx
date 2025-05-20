'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { deleteCookie } from 'cookies-next';
import {
  Box,
  Flex,
  Icon,
  useColorModeValue,
  Link,
  Drawer,
  DrawerContent,
  Text,
  useDisclosure,
  BoxProps,
  FlexProps,
  Button,
  IconButton,
  CloseButton,
  HStack,
} from '@chakra-ui/react';
import {
  ChartBarIcon,
  HomeIcon,
  Bars3Icon,
} from '@heroicons/react/24/outline';
import { ColorModeButton } from '@/components/ui/color-mode';
import React from 'react';

interface LinkItemProps {
  name: string;
  icon: any;
  href: string;
}

const LinkItems: Array<LinkItemProps> = [
  { name: 'Overview', icon: HomeIcon, href: '/dashboard' },
  { name: 'Analytics', icon: ChartBarIcon, href: '/dashboard/analytics' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'black')}>
      <SidebarContent
        onClose={() => onClose}
        display={{ base: 'none', md: 'block' }}
      />
      <Drawer
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full"
      >
        <DrawerContent>
          <SidebarContent onClose={onClose} />
        </DrawerContent>
      </Drawer>
      {/* mobilenav */}
      <MobileNav onOpen={onOpen} />
      <Box ml={{ base: 0, md: 60 }} p="4">
        {children}
      </Box>
    </Box>
  );
}

interface SidebarProps extends BoxProps {
  onClose: () => void;
}

const SidebarContent = ({ onClose, ...rest }: SidebarProps) => {
  return (
    <Box
      transition="3s ease"
      bg={useColorModeValue('white', 'black')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.800')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold" color="brand.500">
          Dashora
        </Text>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      {LinkItems.map((link) => (
        <NavItem key={link.name} icon={link.icon} href={link.href}>
          {link.name}
        </NavItem>
      ))}
    </Box>
  );
};

interface NavItemProps extends FlexProps {
  icon: any;
  href: string;
  children: React.ReactNode;
}

const NavItem = ({ icon, href, children, ...rest }: NavItemProps) => {
  const router = useRouter();
  return (
    <Link
      href={href}
      style={{ textDecoration: 'none' }}
      _focus={{ boxShadow: 'none' }}
    >
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        _hover={{
          bg: 'brand.50',
          color: 'brand.600',
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
            _groupHover={{
              color: 'brand.600',
            }}
          />
        )}
        {children}
      </Flex>
    </Link>
  );
};

interface MobileProps extends FlexProps {
  onOpen: () => void;
}

const MobileNav = ({ onOpen, ...rest }: MobileProps) => {
  const router = useRouter();
  const handleLogout = () => {
    deleteCookie('auth_token');
    router.push('/login');
  };

  return (
    <Flex
      ml={{ base: 0, md: 60 }}
      px={{ base: 4, md: 4 }}
      height="20"
      alignItems="center"
      bg={useColorModeValue('white', 'black')}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue('gray.200', 'gray.800')}
      justifyContent={{ base: 'space-between', md: 'flex-end' }}
      {...rest}
    >
      <IconButton
        display={{ base: 'flex', md: 'none' }}
        onClick={onOpen}
        variant="outline"
        aria-label="open menu"
        icon={<Icon as={Bars3Icon} />}
      />

      <Text
        display={{ base: 'flex', md: 'none' }}
        fontSize="2xl"
        fontWeight="bold"
        color="brand.500"
      >
        Dashora
      </Text>

      <HStack spacing={2}>
        <ColorModeButton />
        <Button
          variant="ghost"
          onClick={handleLogout}
          _hover={{ bg: 'brand.50' }}
        >
          Sign out
        </Button>
      </HStack>
    </Flex>
  );
}; 