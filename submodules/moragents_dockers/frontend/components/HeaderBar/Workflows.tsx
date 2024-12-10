import React, { useState, useEffect, useCallback } from "react";
import {
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
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
  HStack,
  Text,
  Box,
  useToast,
  Divider,
  NumberInput,
  NumberInputField,
  Switch,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from "@chakra-ui/react";
import { ChevronDownIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";

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
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const toast = useToast();

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
    fetchWorkflows();
  }, [fetchWorkflows]);

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
        onClose();
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

  const handleUpdateWorkflow = async (
    id: string,
    updates: Partial<Workflow>
  ) => {
    try {
      const response = await fetch(`http://localhost:8080/workflows/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        toast({
          title: "Workflow updated successfully",
          status: "success",
          duration: 3000,
        });
        fetchWorkflows();
      } else {
        throw new Error("Failed to update workflow");
      }
    } catch (error) {
      console.error("Error updating workflow:", error);
      toast({
        title: "Failed to update workflow",
        status: "error",
        duration: 3000,
      });
    }
  };

  return (
    <>
      <Menu>
        <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
          Workflows
        </MenuButton>
        <MenuList minWidth="300px">
          <Box p={4}>
            <Button colorScheme="green" size="sm" width="full" onClick={onOpen}>
              Create New Workflow
            </Button>
          </Box>
          <Divider />
          {workflows.length > 0 ? (
            workflows.map((workflow) => (
              <MenuItem key={workflow.id} py={4}>
                <HStack width="100%" justify="space-between">
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
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingWorkflow(workflow);
                        onOpen();
                      }}
                    >
                      <EditIcon />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteWorkflow(workflow.id);
                      }}
                    >
                      <DeleteIcon />
                    </Button>
                  </HStack>
                </HStack>
              </MenuItem>
            ))
          ) : (
            <Box p={4}>
              <Text color="gray.500">No workflows created yet</Text>
            </Box>
          )}
        </MenuList>
      </Menu>

      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {editingWorkflow ? "Edit Workflow" : "Create DCA Workflow"}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
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
                <NumberInput
                  value={stepSize}
                  onChange={(value) => setStepSize(value)}
                >
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
                {editingWorkflow ? "Update Workflow" : "Create Workflow"}
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
