import { useState } from "react";
import { Button } from "@chakra-ui/react";
import { FaLock } from "react-icons/fa";
import { ApiCredentialsModal } from "./Modal";

export const ApiCredentialsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button
        leftIcon={<FaLock />}
        onClick={() => setIsOpen(true)}
        size="md"
        colorScheme="gray"
        variant="solid"
        mr={2}
      >
        API Keys
      </Button>

      <ApiCredentialsModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};
