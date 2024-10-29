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
      apiKey: localStorage.getItem("apiKey") || "",
      apiSecret: localStorage.getItem("apiSecret") || "",
      accessToken: localStorage.getItem("accessToken") || "",
      accessTokenSecret: localStorage.getItem("accessTokenSecret") || "",
      bearerToken: localStorage.getItem("bearerToken") || "",
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

  const handleSave = () => {
    Object.entries(credentials).forEach(([key, value]) => {
      localStorage.setItem(key, value);
    });
    onSave();
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="md" mb={2}>
          Twitter API Configuration
        </Heading>
        <Text fontSize="sm" color={textColor}>
          Enter your Twitter API credentials. These can be found in your Twitter
          Developer Portal.
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

      <Button colorScheme="blue" onClick={handleSave} mt={4}>
        Save Twitter Credentials
      </Button>
    </VStack>
  );
};
