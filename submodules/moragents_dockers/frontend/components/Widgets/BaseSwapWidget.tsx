import React, { useState } from "react";
import {
  VStack,
  Box,
  Text,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Button,
  useColorModeValue,
  Heading,
  FormControl,
  FormLabel,
  Container,
  useToast,
  HStack,
} from "@chakra-ui/react";
import { tokens } from "./DCAWidget.constants";

interface SwapConfig {
  fromToken: string;
  toToken: string;
  amount: number;
}

interface BaseSwapWidgetProps {
  onSwap?: (config: SwapConfig) => void;
}

const BaseSwapWidget: React.FC<BaseSwapWidgetProps> = ({ onSwap }) => {
  const toast = useToast();
  const borderColor = useColorModeValue("gray.200", "gray.700");

  const [config, setConfig] = useState<SwapConfig>({
    fromToken: "USDT",
    toToken: "ETH",
    amount: 0,
  });

  const handleSwap = () => {
    if (config.fromToken === config.toToken) {
      toast({
        title: "Invalid Configuration",
        description: "Source and destination tokens must be different",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (config.amount <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Amount must be greater than 0",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    onSwap?.(config);
    toast({
      title: "Swap Initiated",
      description: "Your swap request has been submitted",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Container maxW="container.md">
      <VStack align="stretch" spacing={6}>
        <Box textAlign="center">
          <Heading size="md" mb={3} color="white">
            Base Network Token Swap
          </Heading>
          <Text fontSize="sm" color="white">
            Swap tokens directly on the Base Network
          </Text>
        </Box>

        <VStack
          align="stretch"
          spacing={4}
          p={6}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="md"
        >
          <HStack spacing={4}>
            <FormControl>
              <FormLabel color="white">From Token</FormLabel>
              <Select
                value={config.fromToken}
                onChange={(e) =>
                  setConfig({ ...config, fromToken: e.target.value })
                }
                color="white"
                sx={{
                  "& > option": {
                    color: "black",
                  },
                }}
              >
                {tokens
                  .filter((t) => t.symbol !== config.toToken)
                  .map((token) => (
                    <option key={token.symbol} value={token.symbol}>
                      {token.symbol} - {token.name}
                    </option>
                  ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel color="white">To Token</FormLabel>
              <Select
                value={config.toToken}
                onChange={(e) =>
                  setConfig({ ...config, toToken: e.target.value })
                }
                color="white"
                sx={{
                  "& > option": {
                    color: "black",
                  },
                }}
              >
                {tokens
                  .filter((t) => t.symbol !== config.fromToken)
                  .map((token) => (
                    <option key={token.symbol} value={token.symbol}>
                      {token.symbol} - {token.name}
                    </option>
                  ))}
              </Select>
            </FormControl>
          </HStack>

          <FormControl>
            <FormLabel color="white">Amount</FormLabel>
            <NumberInput
              value={config.amount}
              onChange={(_, value) => setConfig({ ...config, amount: value })}
              min={0}
              precision={6}
            >
              <NumberInputField color="white" />
              <NumberInputStepper>
                <NumberIncrementStepper color="white" />
                <NumberDecrementStepper color="white" />
              </NumberInputStepper>
            </NumberInput>
            <Text fontSize="sm" color="gray.400" mt={1}>
              Amount of {config.fromToken} to swap
            </Text>
          </FormControl>
        </VStack>

        <Button colorScheme="green" onClick={handleSwap} size="md" width="100%">
          Swap Tokens
        </Button>
      </VStack>
    </Container>
  );
};

export default BaseSwapWidget;
