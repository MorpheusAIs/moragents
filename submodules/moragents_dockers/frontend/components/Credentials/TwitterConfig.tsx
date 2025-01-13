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
import { setXCredentials } from "@/services/apiHooks";
import axios from "axios";

interface TwitterCredentials {
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
  bearerToken: string;
}

interface TwitterConfigProps {
  onSave: () => void;
}

export const TwitterConfig: React.FC<TwitterConfigProps> = ({ onSave }) => {
  const [credentials, setCredentials] = useState<TwitterCredentials>({
    apiKey: "",
    apiSecret: "",
    accessToken: "",
    accessTokenSecret: "",
    bearerToken: "",
  });
  const [displayCredentials, setDisplayCredentials] =
    useState<TwitterCredentials>({
      apiKey: "",
      apiSecret: "",
      accessToken: "",
      accessTokenSecret: "",
      bearerToken: "",
    });

  const textColor = useColorModeValue("gray.600", "gray.300");
  const labelColor = useColorModeValue("gray.700", "gray.200");

  const credentialLabels: Record<keyof TwitterCredentials, string> = {
    apiKey: "API Key",
    apiSecret: "API Secret",
    accessToken: "Access Token",
    accessTokenSecret: "Access Token Secret",
    bearerToken: "Bearer Token",
  };

  useEffect(() => {
    const storedCredentials: TwitterCredentials = {
      apiKey: localStorage.getItem("x_api_key") || "",
      apiSecret: localStorage.getItem("x_api_secret") || "",
      accessToken: localStorage.getItem("x_access_token") || "",
      accessTokenSecret: localStorage.getItem("x_access_token_secret") || "",
      bearerToken: localStorage.getItem("x_bearer_token") || "",
    };
    setCredentials(storedCredentials);
    setDisplayCredentials({
      apiKey: obscureCredential(storedCredentials.apiKey),
      apiSecret: obscureCredential(storedCredentials.apiSecret),
      accessToken: obscureCredential(storedCredentials.accessToken),
      accessTokenSecret: obscureCredential(storedCredentials.accessTokenSecret),
      bearerToken: obscureCredential(storedCredentials.bearerToken),
    });
  }, []);

  const obscureCredential = (credential: string) => {
    if (!credential || credential.length <= 5) return credential;
    return "•••••" + credential.slice(-5);
  };

  const handleSave = async () => {
    // Store in localStorage as backup
    localStorage.setItem("x_api_key", credentials.apiKey);
    localStorage.setItem("x_api_secret", credentials.apiSecret);
    localStorage.setItem("x_access_token", credentials.accessToken);
    localStorage.setItem(
      "x_access_token_secret",
      credentials.accessTokenSecret
    );
    localStorage.setItem("x_bearer_token", credentials.bearerToken);

    // Send to backend
    const backendClient = axios.create({
      baseURL: "http://localhost:8080",
    });

    try {
      await setXCredentials(backendClient, {
        api_key: credentials.apiKey,
        api_secret: credentials.apiSecret,
        access_token: credentials.accessToken,
        access_token_secret: credentials.accessTokenSecret,
        bearer_token: credentials.bearerToken,
      });
      onSave();
    } catch (error) {
      console.error("Failed to save X credentials to backend:", error);
    }
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={2}>
          X API Configuration
        </Heading>
        <Text fontSize="sm" color={textColor}>
          Enter your X API credentials. These can be found in your X Developer
          Portal. Please follow the readme to set up these X API keys properly.
        </Text>
      </Box>

      <VStack spacing={4} align="stretch">
        {Object.entries(credentials).map(([key, value]) => (
          <FormControl key={key}>
            <FormLabel color={labelColor} display="flex" alignItems="center">
              {credentialLabels[key as keyof TwitterCredentials]}
              <Text fontSize="xs" color={textColor} ml={2}>
                (
                {displayCredentials[key as keyof TwitterCredentials] ||
                  "Not set"}
                )
              </Text>
            </FormLabel>
            <Input
              type="password"
              placeholder={`Enter new ${
                credentialLabels[key as keyof TwitterCredentials]
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
        Save X API Credentials
      </Button>
    </VStack>
  );
};
