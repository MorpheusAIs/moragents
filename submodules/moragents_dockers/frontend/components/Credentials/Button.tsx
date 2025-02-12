import { useState } from "react";
import { Flex, Text } from "@chakra-ui/react";
import { IconLock } from "@tabler/icons-react";
import { ApiCredentialsModal } from "./Modal";

export const ApiCredentialsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Flex
        as="button"
        align="center"
        gap={3}
        width="100%"
        onClick={() => setIsOpen(true)}
      >
        <IconLock size={20} stroke={1.5} />
        <Text fontSize="14px" color="white">
          API Keys
        </Text>
      </Flex>

      <ApiCredentialsModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};
