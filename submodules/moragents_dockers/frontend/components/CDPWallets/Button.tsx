import { useState } from "react";
import { Flex, Text } from "@chakra-ui/react";
import { IconWallet } from "@tabler/icons-react";
import { CDPWalletsModal } from "./Modal";

export const CDPWalletsButton: React.FC = () => {
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
        <IconWallet size={20} stroke={1.5} />
        <Text fontSize="14px" color="white">
          CDP Wallets
        </Text>
      </Flex>

      <CDPWalletsModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};
