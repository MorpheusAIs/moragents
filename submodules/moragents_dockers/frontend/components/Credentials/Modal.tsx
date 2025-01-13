import { useState } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Grid,
  Box,
  Text,
  useColorModeValue,
  VStack,
  Image,
  Button,
  Flex,
} from "@chakra-ui/react";
import { TwitterConfig } from "@/components/Credentials/TwitterConfig";
import { CoinbaseConfig } from "@/components/Credentials/CoinbaseConfig";
import { OneInchConfig } from "@/components/Credentials/OneInchConfig";
import { IoArrowBack } from "react-icons/io5";

interface ApiOption {
  id: string;
  name: string;
  logo: string;
  component: React.FC<{ onSave: () => void }>;
}

const API_OPTIONS: ApiOption[] = [
  {
    id: "twitter",
    name: "X/Twitter API",
    logo: "/images/x-logo.jpg",
    component: TwitterConfig,
  },
  {
    id: "coinbase",
    name: "Coinbase API",
    logo: "/images/coinbase-logo.png",
    component: CoinbaseConfig,
  },
  {
    id: "oneinch",
    name: "1inch API",
    logo: "/images/one-inch-logo.png",
    component: OneInchConfig,
  },
];

interface ApiCredentialsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ApiCredentialsModal: React.FC<ApiCredentialsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [selectedApi, setSelectedApi] = useState<string | null>(null);
  const bgColor = useColorModeValue("white", "gray.800");
  const cardBgColor = useColorModeValue("gray.50", "gray.700");
  const cardHoverBgColor = useColorModeValue("gray.100", "gray.600");

  const SelectedApiComponent = API_OPTIONS.find(
    (api) => api.id === selectedApi
  )?.component;

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        setSelectedApi(null);
        onClose();
      }}
      size="xl"
      scrollBehavior="inside"
      isCentered
    >
      <ModalOverlay />
      <ModalContent bg={bgColor} maxW={selectedApi ? "2xl" : "4xl"}>
        <ModalHeader>
          {selectedApi && (
            <Button
              leftIcon={<IoArrowBack />}
              variant="ghost"
              size="sm"
              onClick={() => setSelectedApi(null)}
              position="absolute"
              left={4}
              top={3}
            >
              Back
            </Button>
          )}
          <Flex justify="center">
            {selectedApi
              ? API_OPTIONS.find((api) => api.id === selectedApi)?.name
              : "API Credentials"}
          </Flex>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          {!selectedApi ? (
            <VStack spacing={6} align="stretch">
              <Box>
                <Text fontSize="lg" fontWeight="bold" mb={2}>
                  Configure Your API Integrations
                </Text>
                <Text fontSize="md" color="gray.500">
                  Set up your API credentials for various services to enable
                  advanced features and integrations.
                </Text>
              </Box>

              <Grid
                templateColumns="repeat(3, 1fr)"
                gap={4}
                maxH="60vh"
                overflowY="auto"
                p={2}
              >
                {API_OPTIONS.map((api) => (
                  <Box
                    key={api.id}
                    p={4}
                    bg={cardBgColor}
                    borderRadius="lg"
                    cursor="pointer"
                    onClick={() => setSelectedApi(api.id)}
                    _hover={{ bg: cardHoverBgColor }}
                    transition="background-color 0.2s"
                  >
                    <VStack spacing={3}>
                      <Image
                        src={api.logo}
                        alt={`${api.name} logo`}
                        boxSize="50px"
                        objectFit="contain"
                      />
                      <Text fontWeight="medium">{api.name}</Text>
                    </VStack>
                  </Box>
                ))}
              </Grid>
            </VStack>
          ) : (
            SelectedApiComponent && (
              <SelectedApiComponent
                onSave={() => {
                  setSelectedApi(null);
                  onClose();
                }}
              />
            )
          )}
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
