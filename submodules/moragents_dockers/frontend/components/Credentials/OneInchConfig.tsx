import { useState, useEffect } from "react";
import {
  VStack,
  FormControl,
  FormLabel,
  Input,
  Button,
  Text,
  Heading,
  useColorModeValue,
  Box,
} from "@chakra-ui/react";
import { setOneInchCredentials } from "@/services/apiHooks";
import axios from "axios";

interface OneInchCredentials {
  apiKey: string;
}

interface OneInchConfigProps {
  onSave: () => void;
}

export const OneInchConfig: React.FC<OneInchConfigProps> = ({ onSave }) => {
  const [credentials, setCredentials] = useState<OneInchCredentials>({
    apiKey: "",
  });
  const [displayCredentials, setDisplayCredentials] =
    useState<OneInchCredentials>({
      apiKey: "",
    });

  const textColor = useColorModeValue("gray.600", "gray.300");
  const labelColor = useColorModeValue("gray.700", "gray.200");

  const credentialLabels: Record<keyof OneInchCredentials, string> = {
    apiKey: "API Key",
  };

  useEffect(() => {
    const storedCredentials: OneInchCredentials = {
      apiKey: localStorage.getItem("oneinch_api_key") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials({
      apiKey: obscureCredential(storedCredentials.apiKey),
    });
  }, []);

  const obscureCredential = (credential: string) => {
    if (!credential || credential.length <= 5) return credential;
    return "•••••" + credential.slice(-5);
  };

  const handleSave = async () => {
    // Store in localStorage as backup
    Object.entries(credentials).forEach(([key, value]) => {
      localStorage.setItem("oneinch_api_key", value);
    });

    // Send to backend
    const backendClient = axios.create({
      baseURL: "http://localhost:8080",
    });

    try {
      await setOneInchCredentials(backendClient, {
        api_key: credentials.apiKey,
      });
      onSave();
    } catch (error) {
      console.error("Failed to save 1inch API key to backend:", error);
    }
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={2}>
          1inch API Configuration
        </Heading>
        <Text fontSize="sm" color={textColor}>
          Enter your 1inch API key. This can be obtained from the 1inch
          developer portal. The API key is required for accessing 1inch&apos;s
          swap functionality.
        </Text>
      </Box>

      <VStack spacing={4} align="stretch">
        {Object.entries(credentials).map(([key, value]) => (
          <FormControl key={key}>
            <FormLabel color={labelColor} display="flex" alignItems="center">
              {credentialLabels[key as keyof OneInchCredentials]}
              <Text fontSize="xs" color={textColor} ml={2}>
                (
                {displayCredentials[key as keyof OneInchCredentials] ||
                  "Not set"}
                )
              </Text>
            </FormLabel>
            <Input
              type="password"
              placeholder={`Enter new ${
                credentialLabels[key as keyof OneInchCredentials]
              }`}
              value={value}
              onChange={(e) =>
                setCredentials((prev) => ({
                  ...prev,
                  [key]: e.target.value,
                }))
              }
            />
          </FormControl>
        ))}
      </VStack>

      <Button colorScheme="green" onClick={handleSave} mt={4}>
        Save 1inch API Key
      </Button>
    </VStack>
  );
};
