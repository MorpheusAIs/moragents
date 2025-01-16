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
import { setCoinbaseCredentials } from "@/services/apiHooks";
import axios from "axios";

interface CoinbaseCredentials {
  cdpApiKey: string;
  cdpApiSecret: string;
}

interface CoinbaseConfigProps {
  onSave: () => void;
}

export const CoinbaseConfig: React.FC<CoinbaseConfigProps> = ({ onSave }) => {
  const [credentials, setCredentials] = useState<CoinbaseCredentials>({
    cdpApiKey: "",
    cdpApiSecret: "",
  });
  const [displayCredentials, setDisplayCredentials] =
    useState<CoinbaseCredentials>({
      cdpApiKey: "",
      cdpApiSecret: "",
    });

  const textColor = useColorModeValue("gray.600", "gray.300");
  const labelColor = useColorModeValue("gray.700", "gray.200");

  const credentialLabels: Record<keyof CoinbaseCredentials, string> = {
    cdpApiKey: "Coinbase Developer Platform API Key",
    cdpApiSecret: "Coinbase Developer Platform API Secret",
  };

  useEffect(() => {
    const storedCredentials: CoinbaseCredentials = {
      cdpApiKey: localStorage.getItem("coinbase_api_key") || "",
      cdpApiSecret: localStorage.getItem("coinbase_api_secret") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials({
      cdpApiKey: obscureCredential(storedCredentials.cdpApiKey),
      cdpApiSecret: obscureCredential(storedCredentials.cdpApiSecret),
    });
  }, []);

  const obscureCredential = (credential: string) => {
    if (!credential || credential.length <= 5) return credential;
    return "•••••" + credential.slice(-5);
  };

  const handleSave = async () => {
    // Store in localStorage as backup
    localStorage.setItem("coinbase_api_key", credentials.cdpApiKey);
    localStorage.setItem("coinbase_api_secret", credentials.cdpApiSecret);

    // Send to backend
    const backendClient = axios.create({
      baseURL: "http://localhost:8080",
    });

    try {
      await setCoinbaseCredentials(backendClient, {
        cdp_api_key: credentials.cdpApiKey,
        cdp_api_secret: credentials.cdpApiSecret,
      });
      onSave();
    } catch (error) {
      console.error("Failed to save Coinbase credentials to backend:", error);
    }
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={2}>
          Coinbase API Configuration
        </Heading>
        <Text fontSize="sm" color={textColor}>
          Enter your Coinbase Developer Platform API credentials.
        </Text>
      </Box>

      <VStack spacing={4} align="stretch">
        {Object.entries(credentials).map(([key, value]) => (
          <FormControl key={key}>
            <FormLabel color={labelColor} display="flex" alignItems="center">
              {credentialLabels[key as keyof CoinbaseCredentials]}
              <Text fontSize="xs" color={textColor} ml={2}>
                (
                {displayCredentials[key as keyof CoinbaseCredentials] ||
                  "Not set"}
                )
              </Text>
            </FormLabel>
            <Input
              type="password"
              placeholder={`Enter new ${
                credentialLabels[key as keyof CoinbaseCredentials]
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
        Save Coinbase Credentials
      </Button>
    </VStack>
  );
};
