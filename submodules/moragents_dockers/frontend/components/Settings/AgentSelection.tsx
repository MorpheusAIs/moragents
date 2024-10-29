import { useState, useEffect } from "react";
import {
  VStack,
  Checkbox,
  Button,
  Text,
  Heading,
  useColorModeValue,
  Box,
  Badge,
} from "@chakra-ui/react";

interface Agent {
  name: string;
  description: string;
  upload_required: boolean;
}

interface AgentSelectionProps {
  onSave: (agents: string[]) => void;
}

export const AgentSelection: React.FC<AgentSelectionProps> = ({ onSave }) => {
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  const bgHover = useColorModeValue("gray.50", "gray.700");
  const textColor = useColorModeValue("gray.600", "gray.300");
  const boxBg = useColorModeValue("white", "gray.800");

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch("http://localhost:8080/available-agents");
        const data = await response.json();
        setAvailableAgents(data.available_agents);
        setSelectedAgents(data.selected_agents);
      } catch (error) {
        console.error("Failed to fetch available agents:", error);
      }
    };

    fetchAgents();
  }, []);

  const handleAgentToggle = (agentName: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agentName)
        ? prev.filter((name) => name !== agentName)
        : [...prev, agentName]
    );
  };

  const handleSave = async () => {
    try {
      const response = await fetch("http://localhost:8080/selected-agents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ agents: selectedAgents }),
      });
      const data = await response.json();
      if (data.status === "success") {
        onSave(data.agents);
      }
    } catch (error) {
      console.error("Failed to save agent selection:", error);
    }
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={2}>
          Agent Configuration
        </Heading>
        <Text fontSize="sm" color={textColor}>
          Select which agents you want to be available in the system. Only
          selected agents will be loaded and available for use.
        </Text>
      </Box>

      <VStack spacing={3} align="stretch" maxH="400px" overflowY="auto" pr={2}>
        {availableAgents.map((agent) => (
          <Box
            key={agent.name}
            p={4}
            borderRadius="md"
            bg={boxBg}
            _hover={{ bg: bgHover }}
            borderWidth="1px"
          >
            <Checkbox
              isChecked={selectedAgents.includes(agent.name)}
              onChange={() => handleAgentToggle(agent.name)}
              size="md"
            >
              <VStack align="start" spacing={1} ml={2}>
                <Text fontWeight="medium">{agent.name}</Text>
                <Text fontSize="sm" color={textColor}>
                  {agent.description}
                </Text>
                {agent.upload_required && (
                  <Badge colorScheme="blue" fontSize="xs">
                    Requires upload
                  </Badge>
                )}
              </VStack>
            </Checkbox>
          </Box>
        ))}
      </VStack>

      <Button colorScheme="blue" onClick={handleSave} mt={4}>
        Save Agent Selection
      </Button>
    </VStack>
  );
};
