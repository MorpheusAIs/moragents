import { useState } from "react";
import { Button } from "@chakra-ui/react";
import { FaWallet } from "react-icons/fa";
import { CDPWalletsModal } from "./Modal";

export const CDPWalletsButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button
        leftIcon={<FaWallet />}
        onClick={() => setIsOpen(true)}
        size="md"
        colorScheme="gray"
        variant="solid"
        mr={2}
      >
        CDP Wallets
      </Button>

      <CDPWalletsModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};
