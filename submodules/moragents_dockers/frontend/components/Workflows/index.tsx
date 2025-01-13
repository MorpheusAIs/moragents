import React, { useState, useEffect, useCallback } from "react";
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
  FormControl,
  FormLabel,
  Checkbox,
  Container,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  HStack,
  IconButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Input,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { FaRobot } from "react-icons/fa";

interface Workflow {
  id: string;
  name: string;
  description: string;
  action: string;
  params: {
    origin_token: string;
    destination_token: string;
    step_size: number;
    frequency: string;
    price_threshold: number | null;
    pause_on_volatility: boolean;
  };
  interval: number;
  status: string;
  last_run?: string;
  next_run?: string;
}

const tokens = [
  { symbol: "USDC", name: "USD Coin" },
  { symbol: "WETH", name: "Wrapped Ethereum" },
  { symbol: "WBTC", name: "Wrapped Bitcoin" },
  { symbol: "CBETH", name: "Coinbase Wrapped Staked ETH" },
  { symbol: "DAI", name: "Dai Stablecoin" },
];

const frequencies = [
  { value: "minute", label: "Every Minute" },
  { value: "hourly", label: "Hourly" },
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "biweekly", label: "Bi-weekly" },
  { value: "monthly", label: "Monthly" },
];

const FREQUENCIES = {
  minute: 60,
  hourly: 3600,
  daily: 86400,
  weekly: 604800,
  biweekly: 1209600,
  monthly: 2592000,
};

export const Workflows: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const toast = useToast();
  const borderColor = useColorModeValue("gray.200", "gray.700");

  const [config, setConfig] = useState({
    originToken: "USDC",
    destinationToken: "WETH",
    stepSize: 100,
    frequency: "weekly",
    priceThreshold: "",
    pauseOnVolatility: false,
  });

  const fetchWorkflows = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8080/workflows/list");
      const data = await response.json();
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error("Failed to fetch workflows:", error);
      toast({
        title: "Error fetching workflows",
        status: "error",
        duration: 3000,
      });
    }
  }, [toast]);

  useEffect(() => {
    if (isOpen) {
      fetchWorkflows();
    }
  }, [fetchWorkflows, isOpen]);

  const handleCreateWorkflow = async () => {
    if (config.originToken === config.destinationToken) {
      toast({
        title: "Invalid Configuration",
        description: "Origin and destination tokens must be different",
        status: "error",
        duration: 3000,
      });
      return;
    }

    try {
      const workflowData = {
        name: `DCA ${config.originToken} to ${config.destinationToken}`,
        description: `Dollar cost average from ${config.originToken} to ${config.destinationToken}`,
        action: "dca_trade",
        params: {
          origin_token: config.originToken.toLowerCase(),
          destination_token: config.destinationToken.toLowerCase(),
          step_size: config.stepSize,
          frequency: config.frequency,
          price_threshold: config.priceThreshold
            ? Number(config.priceThreshold)
            : null,
          pause_on_volatility: config.pauseOnVolatility,
        },
        interval: FREQUENCIES[config.frequency as keyof typeof FREQUENCIES],
      };

      const response = await fetch("http://localhost:8080/workflows/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        toast({
          title: "Workflow created successfully",
          status: "success",
          duration: 3000,
        });
        fetchWorkflows();
        setIsOpen(false);
      } else {
        throw new Error("Failed to create workflow");
      }
    } catch (error) {
      console.error("Error creating workflow:", error);
      toast({
        title: "Failed to create workflow",
        status: "error",
        duration: 3000,
      });
    }
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8080/workflows/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast({
          title: "Workflow deleted successfully",
          status: "success",
          duration: 3000,
        });
        fetchWorkflows();
      } else {
        throw new Error("Failed to delete workflow");
      }
    } catch (error) {
      console.error("Error deleting workflow:", error);
      toast({
        title: "Failed to delete workflow",
        status: "error",
        duration: 3000,
      });
    }
  };

  const WorkflowsList = () => (
    <VStack spacing={4} align="stretch">
      {workflows.length > 0 ? (
        workflows.map((workflow) => (
          <Box
            key={workflow.id}
            p={4}
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="md"
          >
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <Text color="white" fontWeight="semibold">
                  {workflow.name}
                </Text>
                <Text color="gray.400" fontSize="sm">
                  Status: {workflow.status}
                </Text>
                {workflow.next_run && (
                  <Text color="gray.500" fontSize="xs">
                    Next run: {new Date(workflow.next_run).toLocaleString()} UTC
                  </Text>
                )}
              </VStack>
              <IconButton
                aria-label="Delete workflow"
                icon={<DeleteIcon />}
                onClick={() => handleDeleteWorkflow(workflow.id)}
                variant="ghost"
                colorScheme="red"
                size="sm"
              />
            </HStack>
          </Box>
        ))
      ) : (
        <Text color="gray.500" textAlign="center">
          No workflows created yet
        </Text>
      )}
    </VStack>
  );

  const CreateWorkflowForm = () => (
    <VStack spacing={4}>
      <HStack spacing={4} width="100%">
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
            {tokens
              .filter((t) => t.symbol !== config.destinationToken)
              .map((token) => (
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
            {tokens
              .filter((t) => t.symbol !== config.originToken)
              .map((token) => (
                <option key={token.symbol} value={token.symbol}>
                  {token.symbol} - {token.name}
                </option>
              ))}
          </Select>
        </FormControl>
      </HStack>

      <FormControl>
        <FormLabel color="white">Investment Step Size</FormLabel>
        <Input
          type="number"
          step="any"
          min="0"
          color="white"
          value={config.stepSize}
          onChange={(e) =>
            setConfig({
              ...config,
              stepSize: e.target.value ? parseFloat(e.target.value) : 0,
            })
          }
        />
        <Text fontSize="sm" color="gray.400" mt={1}>
          Amount to invest at each interval
        </Text>
      </FormControl>

      <FormControl>
        <FormLabel color="white">Frequency</FormLabel>
        <Select
          value={config.frequency}
          onChange={(e) => setConfig({ ...config, frequency: e.target.value })}
          color="white"
          sx={{
            "& > option": {
              color: "black",
            },
          }}
        >
          {frequencies.map((freq) => (
            <option key={freq.value} value={freq.value}>
              {freq.label}
            </option>
          ))}
        </Select>
      </FormControl>

      <FormControl>
        <FormLabel color="white">Price Threshold (Optional)</FormLabel>
        <NumberInput
          value={config.priceThreshold}
          onChange={(_, valueAsNumber) =>
            setConfig({ ...config, priceThreshold: valueAsNumber.toString() })
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

      <Button
        onClick={handleCreateWorkflow}
        width="100%"
        mt={6}
        colorScheme="green"
      >
        Create Workflow
      </Button>
    </VStack>
  );

  return (
    <>
      <Button
        leftIcon={<FaRobot />}
        onClick={() => setIsOpen(true)}
        size="md"
        colorScheme="gray"
        variant="solid"
      >
        Workflows
      </Button>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="xl">
        <ModalOverlay />
        <ModalContent bg="gray.900">
          <ModalHeader color="white" textAlign="center">
            Workflows
          </ModalHeader>
          <ModalCloseButton color="white" />
          <ModalBody pb={6}>
            <Container maxW="container.md">
              <Tabs variant="enclosed" colorScheme="blue" isFitted>
                <TabList mb={4}>
                  <Tab
                    color="white"
                    _selected={{ color: "white", bg: "blue.500" }}
                  >
                    Active Workflows
                  </Tab>
                  <Tab
                    color="white"
                    _selected={{ color: "white", bg: "blue.500" }}
                  >
                    Create New
                  </Tab>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <WorkflowsList />
                  </TabPanel>
                  <TabPanel>
                    <CreateWorkflowForm />
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </Container>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default Workflows;
