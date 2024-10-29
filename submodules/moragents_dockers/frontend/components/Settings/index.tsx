import { useState } from "react";
import { FaCog } from "react-icons/fa";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Button,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
} from "@chakra-ui/react";
import { TwitterConfig } from "./TwitterConfig";
import { CoinbaseConfig } from "./CoinbaseConfig";
import { AgentSelection } from "./AgentSelection";

export const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const bgColor = useColorModeValue("white", "gray.800");

  return (
    <>
      <Button
        leftIcon={<FaCog />}
        onClick={() => setIsOpen(true)}
        size="md"
        colorScheme="gray"
        variant="solid"
      >
        Settings
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
          <ModalHeader>Settings</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Tabs variant="enclosed" isFitted>
              <TabList mb={4}>
                <Tab>Twitter API</Tab>
                <Tab>Coinbase API</Tab>
                <Tab>Agents</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <TwitterConfig onSave={() => setIsOpen(false)} />
                </TabPanel>
                <TabPanel>
                  <CoinbaseConfig onSave={() => setIsOpen(false)} />
                </TabPanel>
                <TabPanel>
                  <AgentSelection onSave={() => setIsOpen(false)} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
