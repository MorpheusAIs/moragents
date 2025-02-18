import React, { FC, useState } from "react";
import {
  VStack,
  Box,
  Text,
  Button,
  HStack,
  FormControl,
  Input,
  InputGroup,
  InputRightAddon,
  IconButton,
  Collapse,
} from "@chakra-ui/react";
import { InfoIcon } from "@chakra-ui/icons";
import { ArrowLeftRight } from "lucide-react";
import { useAccount } from "wagmi";
import { useSwapTransaction } from "@/components/Agents/Swaps/CustomMessages/useSwapTransaction";

interface OneInchSwapMessageProps {
  content: any;
  metadata: {
    src?: string;
    dst?: string;
    src_address?: string;
    dst_address?: string;
    src_amount?: number;
    dst_amount?: number;
  };
}

const OneInchSwapMessage: FC<OneInchSwapMessageProps> = ({
  content,
  metadata = {},
}) => {
  const { address } = useAccount();
  const { handleSwap, handleCancel, isLoading } = useSwapTransaction();
  const [slippage, setSlippage] = useState(0.1);
  const [showForm, setShowForm] = useState(false);

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
    <Box width="100%" mb={4}>
      <Box display="inline-flex" alignItems="center" gap={2}>
        <Text color="white">{content}</Text>
        <IconButton
          onClick={() => setShowForm(!showForm)}
          variant="ghost"
          size="sm"
          color="gray.400"
          _hover={{ color: "blue.400" }}
          aria-label="Configure 1inch swap"
          icon={<ArrowLeftRight size={16} />}
        />
      </Box>

      <Collapse in={showForm} animateOpacity>
        <Box
          mt={4}
          p={4}
          bg="gray.900"
          borderRadius="lg"
          borderWidth="1px"
          borderColor="gray.700"
        >
          <Box bg="#111613" p={4} borderRadius="md">
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
                onClick={() => {
                  handleCancel(0);
                  setShowForm(false);
                }}
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
        </Box>
      </Collapse>
    </Box>
  );
};

export default OneInchSwapMessage;
