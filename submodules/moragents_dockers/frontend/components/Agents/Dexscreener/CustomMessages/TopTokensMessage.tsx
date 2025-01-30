import React from "react";
import {
  Box,
  SimpleGrid,
  Image,
  Text,
  Link,
  Flex,
  IconButton,
  Tooltip,
} from "@chakra-ui/react";
import {
  FaTwitter,
  FaTelegram,
  FaGlobe,
  FaLink,
  FaExternalLinkAlt,
} from "react-icons/fa";
import { SiCoinmarketcap } from "react-icons/si";
import { CopyIcon } from "@chakra-ui/icons";

export const TopTokensMessage = ({ metadata }: { metadata: any }) => {
  const { chain_id, tokens } = metadata || {};

  // We’ll force a darker background and text color for a "dark mode" style.
  const cardBg = "gray.800";
  const textColor = "whiteAlpha.900";

  // Truncate a token address
  const truncateAddress = (address: string, start = 6, end = 6) => {
    if (!address) return "";
    if (address.length <= start + end) return address;
    return `${address.slice(0, start)}...${address.slice(-end)}`;
  };

  // Copy to clipboard
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  // A helper to pick an icon based on link label or type
  const getLinkIcon = (labelOrType = "") => {
    const val = labelOrType.toLowerCase();
    if (val.includes("twitter")) return <FaTwitter />;
    if (val.includes("telegram")) return <FaTelegram />;
    if (val.includes("website")) return <FaGlobe />;
    if (val.includes("coinmarketcap") || val.includes("cmc"))
      return <SiCoinmarketcap />;
    return <FaLink />;
  };

  return (
    <Box width="100%" color={textColor}>
      {/* Just a small heading-like text, not too large */}
      <Box textAlign="center" fontSize="xl" mb={4} fontWeight="bold">
        {chain_id ? `Tokens on ${chain_id.toUpperCase()}` : "Tokens"}
      </Box>

      <SimpleGrid
        columns={[1, 2, 3, 4, 5]}
        spacing={5}
        justifyItems="center"
        maxWidth="1200px"
        mx="auto"
      >
        {tokens?.map((token: any, index: number) => (
          <Box
            key={index}
            bg={cardBg}
            border="1px solid"
            borderColor="gray.700"
            borderRadius="10px"
            padding="1.5rem"
            maxW="260px"
            width="100%"
            _hover={{ borderColor: "blue.500" }}
            transition="all 0.15s ease"
          >
            {/* Token icon */}
            {token.icon && (
              <Flex justify="center" mb={3}>
                <Image
                  src={token.icon}
                  alt={token.tokenAddress}
                  boxSize="64px"
                  objectFit="contain"
                />
              </Flex>
            )}

            {/* Token address */}
            <Flex align="center" justify="center" mb={2}>
              <Text fontWeight="semibold" mr={2} textAlign="center">
                {truncateAddress(token.tokenAddress)}
              </Text>
              <Tooltip label="Copy address" placement="top">
                <IconButton
                  aria-label="Copy address"
                  icon={<CopyIcon />}
                  size="xs"
                  variant="ghost"
                  color="gray.400"
                  onClick={() => handleCopy(token.tokenAddress)}
                  _hover={{ color: "blue.400" }}
                />
              </Tooltip>
            </Flex>

            {/* Description */}
            {token.description && (
              <Text
                fontSize="sm"
                textAlign="center"
                mb={3}
                noOfLines={3}
                wordBreak="break-word"
                color="gray.300"
              >
                {token.description}
              </Text>
            )}

            {/* Primary DexScreener link */}
            {token.url && (
              <Flex justify="center" mb={3}>
                <Link
                  href={token.url}
                  target="_blank"
                  display="inline-flex"
                  alignItems="center"
                  color="blue.400"
                  fontWeight="medium"
                  fontSize="sm"
                  _hover={{ textDecoration: "underline" }}
                >
                  DexScreener
                  <Box as="span" ml={1}>
                    <FaExternalLinkAlt fontSize="0.8rem" />
                  </Box>
                </Link>
              </Flex>
            )}

            {/* Additional links (icons) */}
            {token.links && token.links.length > 0 && (
              <Flex gap={3} mb={3} flexWrap="wrap" justify="center">
                {token.links.map((link: any, linkIdx: number) => {
                  const label = link.label || link.type || "Link";
                  return (
                    <Link
                      key={linkIdx}
                      href={link.url}
                      target="_blank"
                      color="blue.400"
                      fontSize="xl"
                      _hover={{ color: "blue.300" }}
                    >
                      {getLinkIcon(label)}
                    </Link>
                  );
                })}
              </Flex>
            )}

            {/* Total amount */}
            {token.totalAmount && (
              <Text fontSize="sm" textAlign="center" color="gray.400">
                Total Amount: <strong>{token.totalAmount}</strong>
              </Text>
            )}
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};
