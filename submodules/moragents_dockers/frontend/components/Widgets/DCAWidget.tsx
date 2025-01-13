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
  Checkbox,
  Divider,
  HStack,
  Container,
  useToast,
  Collapse,
  useDisclosure,
  Input,
} from "@chakra-ui/react";
import {
  BASE_AVAILABLE_TOKENS,
  DCA_AVAILABLE_FREQUENCIES,
} from "@/services/constants";

interface DCAConfig {
  originToken: string;
  destinationToken: string;
  stepSize: number;
  totalInvestmentAmount?: number;
  frequency: string;
  maxPurchaseAmount?: number;
  priceThreshold?: number;
  pauseOnVolatility: boolean;
}

const DCAWidget: React.FC = () => {
  const toast = useToast();
  const borderColor = useColorModeValue("gray.200", "gray.700");
  const { isOpen, onToggle } = useDisclosure();

  const [config, setConfig] = useState<DCAConfig>({
    originToken: "usdc",
    destinationToken: "weth",
    stepSize: 100,
    frequency: "weekly",
    pauseOnVolatility: false,
  });

  const handleSave = async () => {
    if (config.originToken === config.destinationToken) {
      toast({
        title: "Invalid Configuration",
        description: "Origin and destination tokens must be different",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (config.stepSize <= 0) {
      toast({
        title: "Invalid Step Size",
        description: "Step size must be greater than 0",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8080/dca/create_strategy",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(config),
        }
      );

      const data = await response.json();

      if (data.status === "success") {
        toast({
          title: "Strategy Created",
          description: "Your DCA strategy has been created successfully",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      toast({
        title: "Strategy Creation Failed",
        description:
          error instanceof Error
            ? error.message
            : "Failed to create DCA strategy",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const calculateTimeToCompletion = () => {
    const frequencyInDays =
      {
        hourly: 1 / 24,
        daily: 1,
        weekly: 7,
        biweekly: 14,
        monthly: 30,
      }[config.frequency] || 0;

    const totalPurchases = config.totalInvestmentAmount
      ? Math.ceil(config.totalInvestmentAmount / config.stepSize)
      : null;

    if (!totalPurchases) return "Ongoing strategy";

    const daysToComplete = totalPurchases * frequencyInDays;

    if (daysToComplete < 1) return "Less than a day";
    if (daysToComplete < 30) return `${Math.ceil(daysToComplete)} days`;
    if (daysToComplete < 365) return `${Math.ceil(daysToComplete / 30)} months`;
    return `${Math.round((daysToComplete / 365) * 10) / 10} years`;
  };

  return (
    <Container maxW="container.md">
      <VStack align="stretch" spacing={6}>
        <Box textAlign="center">
          <Heading size="md" mb={3} color="white">
            DCA Strategy Configuration
          </Heading>
          <Text fontSize="sm" color="white">
            Configure your automated Dollar Cost Averaging strategy settings
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
          {/* From / To selection */}
          <HStack spacing={4}>
            <FormControl>
              <FormLabel color="white">From (Origin)</FormLabel>
              <Select
                value={config.originToken}
                onChange={(e) =>
                  setConfig({ ...config, originToken: e.target.value })
                }
                color="white"
                sx={{
                  "& > option": {
                    color: "black",
                  },
                }}
              >
                {BASE_AVAILABLE_TOKENS.filter(
                  (t) => t.symbol !== config.destinationToken
                ).map((token) => (
                  <option key={token.symbol} value={token.symbol}>
                    {token.symbol} - {token.name}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel color="white">To (Destination)</FormLabel>
              <Select
                value={config.destinationToken}
                onChange={(e) =>
                  setConfig({ ...config, destinationToken: e.target.value })
                }
                color="white"
                sx={{
                  "& > option": {
                    color: "black",
                  },
                }}
              >
                {BASE_AVAILABLE_TOKENS.filter(
                  (t) => t.symbol !== config.originToken
                ).map((token) => (
                  <option key={token.symbol} value={token.symbol}>
                    {token.symbol} - {token.name}
                  </option>
                ))}
              </Select>
            </FormControl>
          </HStack>

          {/* Step size */}
          <FormControl>
            <FormLabel color="white">Investment Step Size</FormLabel>
            <NumberInput
              value={config.stepSize}
              onChange={(_, valueAsNumber) =>
                setConfig({ ...config, stepSize: valueAsNumber })
              }
              min={1}
            >
              <NumberInputField color="white" />
              <NumberInputStepper>
                <NumberIncrementStepper color="white" />
                <NumberDecrementStepper color="white" />
              </NumberInputStepper>
            </NumberInput>
            <Text fontSize="sm" color="gray.400" mt={1}>
              Amount to invest at each interval
            </Text>
          </FormControl>

          {/* Total Investment Amount */}
          <FormControl>
            <FormLabel color="white">
              Total Investment Amount (Optional)
            </FormLabel>
            <Input
              type="number"
              step="any" // Allows any decimal input
              min="0"
              color="white"
              placeholder="No limit"
              value={config.totalInvestmentAmount ?? ""}
              onChange={(e) =>
                setConfig({
                  ...config,
                  // Store as string so partial decimals like "1." won't break
                  totalInvestmentAmount: e.target.value,
                })
              }
            />
            <Text fontSize="sm" color="gray.400" mt={1}>
              Total amount to invest over time
            </Text>
          </FormControl>

          {/* Frequency */}
          <FormControl>
            <FormLabel color="white">Frequency</FormLabel>
            <Select
              value={config.frequency}
              onChange={(e) =>
                setConfig({ ...config, frequency: e.target.value })
              }
              color="white"
              sx={{
                "& > option": {
                  color: "black",
                },
              }}
            >
              {DCA_AVAILABLE_FREQUENCIES.map((freq) => (
                <option key={freq.value} value={freq.value}>
                  {freq.label}
                </option>
              ))}
            </Select>
          </FormControl>

          {/* Advanced Settings */}
          <Button
            onClick={onToggle}
            variant="ghost"
            color="white"
            _hover={{ bg: "gray.800" }}
          >
            {isOpen ? "Hide Advanced Settings" : "Show Advanced Settings"}
          </Button>

          <Collapse in={isOpen}>
            <Box>
              <Divider borderColor="white" mb={4} />
              <VStack align="stretch" spacing={4}>
                {/* Max Purchase Amount */}
                <FormControl>
                  <FormLabel color="white">
                    Maximum Purchase Amount (Optional)
                  </FormLabel>
                  <NumberInput
                    value={config.maxPurchaseAmount ?? ""}
                    onChange={(_, valueAsNumber) =>
                      setConfig({ ...config, maxPurchaseAmount: valueAsNumber })
                    }
                    min={1}
                  >
                    <NumberInputField color="white" placeholder="No maximum" />
                    <NumberInputStepper>
                      <NumberIncrementStepper color="white" />
                      <NumberDecrementStepper color="white" />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                {/* Price Threshold */}
                <FormControl>
                  <FormLabel color="white">
                    Price Threshold (Optional)
                  </FormLabel>
                  <NumberInput
                    value={config.priceThreshold ?? ""}
                    onChange={(_, valueAsNumber) =>
                      setConfig({ ...config, priceThreshold: valueAsNumber })
                    }
                  >
                    <NumberInputField
                      placeholder="Only buy below this price"
                      color="white"
                    />
                    <NumberInputStepper>
                      <NumberIncrementStepper color="white" />
                      <NumberDecrementStepper color="white" />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>

                {/* Volatility Checkbox */}
                <Checkbox
                  isChecked={config.pauseOnVolatility}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      pauseOnVolatility: e.target.checked,
                    })
                  }
                  color="white"
                  sx={{
                    "[data-checked]": {
                      backgroundColor: "white !important",
                      borderColor: "white !important",
                    },
                    "& .chakra-checkbox__control": {
                      borderColor: "white",
                    },
                  }}
                >
                  Pause strategy during high volatility
                </Checkbox>
              </VStack>
            </Box>
          </Collapse>
        </VStack>

        {/* Time to completion */}
        <Text color="white" textAlign="center" fontSize="sm">
          Estimated time to completion: {calculateTimeToCompletion()}
        </Text>

        {/* Execute Strategy */}
        <Button colorScheme="green" onClick={handleSave} size="md" width="100%">
          Execute Strategy
        </Button>
      </VStack>
    </Container>
  );
};

export default DCAWidget;
