import { useState, useEffect } from "react";
import {
  VStack,
  Box,
  Checkbox,
  Button,
  Text,
  useToast,
} from "@chakra-ui/react";
import styles from "./AgentSelection.module.css";

interface Agent {
  name: string;
  description: string;
  human_readable_name: string;
}

interface AgentSelectionProps {
  onSave: (agents: string[]) => void;
}

export const AgentSelection: React.FC<AgentSelectionProps> = ({ onSave }) => {
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const toast = useToast();

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch("http://localhost:8888/agents/available");
        const data = await response.json();
        setAvailableAgents(data.available_agents);
        setSelectedAgents(data.selected_agents);
      } catch (error) {
        console.error("Failed to fetch agents:", error);
      }
    };

    fetchAgents();
  }, []);

  const handleAgentToggle = (agentName: string) => {
    setSelectedAgents((prev) => {
      if (prev.includes(agentName)) {
        return prev.filter((name) => name !== agentName);
      } else {
        if (prev.length >= 6) {
          toast({
            title: "Maximum agents selected",
            description: "You can only select up to 6 agents at a time",
            status: "warning",
            duration: 3000,
            isClosable: true,
            position: "top-right",
            variant: "subtle",
            bg: "#080808",
            color: "white",
          });
          return prev;
        }
        return [...prev, agentName];
      }
    });
  };

  const handleSave = async () => {
    try {
      const response = await fetch("http://localhost:8888/agents/selected", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ agents: selectedAgents }),
      });
      const data = await response.json();
      if (data.status === "success") {
        onSave(data.agents);
        window.location.reload();
      }
    } catch (error) {
      console.error("Failed to save selection:", error);
    }
  };

  return (
    <VStack spacing={4} align="stretch">
      <Text className={styles.description}>
        Select which agents you want to be available in the system. For
        performance reasons, only 6 agents can be selected at a time.
      </Text>

      <Box className={styles.agentList}>
        <VStack spacing={2} align="stretch">
          {availableAgents.map((agent) => (
            <Box key={agent.name} className={styles.agentItem}>
              <Checkbox
                isChecked={selectedAgents.includes(agent.name)}
                onChange={() => handleAgentToggle(agent.name)}
                width="100%"
                className={styles.checkbox}
              >
                <VStack align="start" spacing={1} ml={3}>
                  <Text className={styles.agentName}>
                    {agent.human_readable_name}
                  </Text>
                  <Text className={styles.agentDescription}>
                    {agent.description}
                  </Text>
                </VStack>
              </Checkbox>
            </Box>
          ))}
        </VStack>
      </Box>

      <Button onClick={handleSave} className={styles.saveButton}>
        Save Configuration
      </Button>
    </VStack>
  );
};
