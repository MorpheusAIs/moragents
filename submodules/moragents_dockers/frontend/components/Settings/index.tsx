import { useState } from "react";
import { Flex, Text } from "@chakra-ui/react";
import { IconSettings } from "@tabler/icons-react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
} from "@chakra-ui/react";
import { GeneralSettings } from "./GeneralSettings";
import { AgentSelection } from "./AgentSelection";

export const SettingsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const bgColor = useColorModeValue("white", "gray.800");

  return (
    <>
      <Flex
        as="button"
        align="center"
        gap={3}
        width="100%"
        onClick={() => setIsOpen(true)}
      >
        <IconSettings size={20} stroke={1.5} />
        <Text fontSize="14px" color="white">
          Agent Configurations
        </Text>
      </Flex>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        size="xl"
        scrollBehavior="inside"
        isCentered
      >
        <ModalOverlay />
        <ModalContent bg={bgColor}>
          <ModalHeader>Settings</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Tabs variant="enclosed" isFitted>
              <TabList mb={4}>
                <Tab>General</Tab>
                <Tab>Agents</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <GeneralSettings onSave={() => setIsOpen(false)} />
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
