import React, { FC } from "react";
import {
  VStack,
  Box,
  Text,
  Button,
  Container,
  HStack,
  Heading,
  FormControl,
  Input,
  InputGroup,
  InputRightAddon,
  IconButton,
} from "@chakra-ui/react";
import { InfoIcon } from "@chakra-ui/icons";
import { useAccount } from "wagmi";
import { useSwapTransaction } from "@/components/Agents/Swaps/useSwapTransaction";

interface OneInchSwapWidgetProps {
  metadata: {
    src?: string;
    dst?: string;
    src_address?: string;
    dst_address?: string;
    src_amount?: number;
    dst_amount?: number;
  };
}

const OneInchSwapWidget: FC<OneInchSwapWidgetProps> = ({ metadata = {} }) => {
  const { address } = useAccount();
  const { handleSwap, handleCancel, isLoading } = useSwapTransaction();
  const [slippage, setSlippage] = React.useState(0.1);

  // Default values for metadata fields
  const src = metadata.src || "ETH";
  const dst = metadata.dst || "USDC";
  const srcAmount = metadata.src_amount || 0;
  const dstAmount = metadata.dst_amount || 0;
  const srcAddress =
    metadata.src_address || "0x0000000000000000000000000000000000000000";
  const dstAddress =
    metadata.dst_address || "0x0000000000000000000000000000000000000000";

  return (
    <Container maxW="container.md">
      <VStack align="stretch" spacing={6}>
        <Box textAlign="center">
          <Heading size="md" mb={3} color="white">
            1inch Network Token Swap
          </Heading>
          <Text fontSize="sm" color="white">
            Swap tokens using 1inch aggregator
          </Text>
        </Box>

        <Box
          p={6}
          borderWidth="1px"
          borderColor="gray.700"
          borderRadius="md"
          bg="#111613"
        >
          <HStack spacing={4} align="stretch">
            <Box flex="1" borderRight="1px solid #CCCECD" pr={4}>
              <VStack align="start">
                <Text color="white">You Pay</Text>
                <HStack>
                  <Text color="#9A9C9B" fontSize="16px">
                    {srcAmount}
                  </Text>
                  <Text color="white">{src}</Text>
                </HStack>
              </VStack>
            </Box>

            <Box flex="1" borderRight="1px solid #CCCECD" px={4}>
              <VStack align="start">
                <Text color="white">You Receive</Text>
                <HStack>
                  <Text color="#9A9C9B" fontSize="16px">
                    {dstAmount.toFixed(4)}
                  </Text>
                  <Text color="white">{dst}</Text>
                </HStack>
              </VStack>
            </Box>

            <Box flex="1" pl={4}>
              <FormControl>
                <HStack mb={1}>
                  <Text color="white" fontSize="16px">
                    Slippage
                  </Text>
                  <IconButton
                    aria-label="Info"
                    icon={<InfoIcon />}
                    variant="ghost"
                    size="sm"
                    color="white"
                  />
                </HStack>
                <InputGroup>
                  <Input
                    type="number"
                    value={slippage}
                    onChange={(e) => setSlippage(Number(e.target.value))}
                    color="white"
                    border="1px solid #676B68"
                  />
                  <InputRightAddon bg="transparent" color="#9A9C9B">
                    %
                  </InputRightAddon>
                </InputGroup>
                <Text color="#676B68" fontSize="10px" mt={1}>
                  Using 1inch
                </Text>
              </FormControl>
            </Box>
          </HStack>

          <HStack justify="flex-end" mt={6} spacing={4}>
            <Button
              variant="ghost"
              onClick={() => handleCancel(0)}
              color="white"
              _hover={{ bg: "transparent", color: "#59F886" }}
            >
              Cancel
            </Button>
            <Button
              variant="greenCustom"
              onClick={() =>
                handleSwap({
                  dstAmount: dstAmount.toString(),
                  tx: {
                    data: "0x",
                    from: address || "",
                    gas: 0,
                    gasPrice: "0",
                    to: dstAddress,
                    value: srcAmount.toString(),
                  },
                })
              }
              isLoading={isLoading}
              disabled={!address}
            >
              Swap
            </Button>
          </HStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default OneInchSwapWidget;
