import React, { useState, useEffect, useCallback } from "react";
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  Text,
  useToast,
  NumberInput,
  NumberInputField,
  Switch,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
  Box,
  HStack,
  IconButton,
} from "@chakra-ui/react";
import { DeleteIcon, EditIcon } from "@chakra-ui/icons";
import { FaRobot } from "react-icons/fa";

interface Workflow {
  id: string;
  name: string;
  description: string;
  action: string;
  params: any;
  interval: number;
  status: string;
  last_run?: string;
  next_run?: string;
}

const FREQUENCIES = {
  hourly: 3600,
  daily: 86400,
  weekly: 604800,
  biweekly: 1209600,
  monthly: 2592000,
};

export const Workflows: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const toast = useToast();
  const bgColor = useColorModeValue("white", "gray.800");

  // DCA Form State
  const [originToken, setOriginToken] = useState("ETH");
  const [destinationToken, setDestinationToken] = useState("USDC");
  const [stepSize, setStepSize] = useState("0.1");
  const [frequency, setFrequency] = useState("weekly");
  const [priceThreshold, setPriceThreshold] = useState("");
  const [pauseOnVolatility, setPauseOnVolatility] = useState(false);
  const [selectedWalletId, setSelectedWalletId] = useState("");

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
    try {
      const workflowData = {
        name: `DCA ${originToken} to ${destinationToken}`,
        description: `Dollar cost average from ${originToken} to ${destinationToken}`,
        action: "dca_trade",
        params: {
          origin_token: originToken,
          destination_token: destinationToken,
          step_size: stepSize,
          frequency,
          price_threshold: priceThreshold || null,
          pause_on_volatility: pauseOnVolatility,
          wallet_id: selectedWalletId,
        },
        interval: FREQUENCIES[frequency as keyof typeof FREQUENCIES],
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
    <VStack spacing={4} align="stretch" width="100%">
      {workflows.length > 0 ? (
        workflows.map((workflow) => (
          <Box
            key={workflow.id}
            p={4}
            borderWidth="1px"
            borderRadius="md"
            position="relative"
          >
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <Text fontWeight="bold">{workflow.name}</Text>
                <Text fontSize="sm" color="gray.500">
                  Status: {workflow.status}
                </Text>
                {workflow.next_run && (
                  <Text fontSize="xs" color="gray.400">
                    Next run: {new Date(workflow.next_run).toLocaleString()} UTC
                  </Text>
                )}
              </VStack>
              <HStack>
                <IconButton
                  aria-label="Edit workflow"
                  icon={<EditIcon />}
                  size="sm"
                  variant="ghost"
                  onClick={() => setEditingWorkflow(workflow)}
                />
                <IconButton
                  aria-label="Delete workflow"
                  icon={<DeleteIcon />}
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={() => handleDeleteWorkflow(workflow.id)}
                />
              </HStack>
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
      <FormControl>
        <FormLabel>Origin Token</FormLabel>
        <Input
          value={originToken}
          onChange={(e) => setOriginToken(e.target.value)}
        />
      </FormControl>
      <FormControl>
        <FormLabel>Destination Token</FormLabel>
        <Input
          value={destinationToken}
          onChange={(e) => setDestinationToken(e.target.value)}
        />
      </FormControl>
      <FormControl>
        <FormLabel>Step Size</FormLabel>
        <NumberInput value={stepSize} onChange={(value) => setStepSize(value)}>
          <NumberInputField />
        </NumberInput>
      </FormControl>
      <FormControl>
        <FormLabel>Frequency</FormLabel>
        <Select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value)}
        >
          {Object.keys(FREQUENCIES).map((freq) => (
            <option key={freq} value={freq}>
              {freq.charAt(0).toUpperCase() + freq.slice(1)}
            </option>
          ))}
        </Select>
      </FormControl>
      <FormControl>
        <FormLabel>Price Threshold (Optional)</FormLabel>
        <NumberInput
          value={priceThreshold}
          onChange={(value) => setPriceThreshold(value)}
        >
          <NumberInputField />
        </NumberInput>
      </FormControl>
      <FormControl>
        <FormLabel>Pause on High Volatility</FormLabel>
        <Switch
          isChecked={pauseOnVolatility}
          onChange={(e) => setPauseOnVolatility(e.target.checked)}
        />
      </FormControl>
      <FormControl>
        <FormLabel>Wallet ID</FormLabel>
        <Input
          value={selectedWalletId}
          onChange={(e) => setSelectedWalletId(e.target.value)}
        />
      </FormControl>
      <Button
        colorScheme="blue"
        width="full"
        mt={4}
        onClick={handleCreateWorkflow}
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
        mr={2}
      >
        Workflows
      </Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        size="xl"
        scrollBehavior="inside"
        isCentered
      >
        <ModalOverlay />
        <ModalContent bg={bgColor} textAlign="center">
          <ModalHeader>Workflows</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Tabs variant="enclosed" isFitted>
              <TabList mb={4}>
                <Tab>Active Workflows</Tab>
                <Tab>Create New</Tab>
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
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default Workflows;
