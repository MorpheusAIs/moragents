import React, { FC, useState } from "react";
import {
  Flex,
  Input,
  InputGroup,
  InputLeftAddon,
  InputRightAddon,
  IconButton,
} from "@chakra-ui/react";
import { AttachmentIcon } from "@chakra-ui/icons";
import { SendIcon } from "../CustomIcon/SendIcon";
import { availableAgents } from "../../config";

type ChatInputProps = {
  onSubmit: (message: string, file: File | null) => Promise<void>;
  selectedAgent: string;
  disabled: boolean;
};

export const ChatInput: FC<ChatInputProps> = ({
  onSubmit,
  selectedAgent,
  disabled,
}) => {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const agentSupportsFileUploads =
    availableAgents[selectedAgent]?.supportsFiles || false;

  const handleSubmit = async () => {
    if (!message && !file) return;
    await onSubmit(message, file);
    setMessage("");
    setFile(null);
  };

  return (
    <Flex mt={4} sx={{ pl: 6, pr: 6 }}>
      <InputGroup
        sx={{ pt: 2, pb: 2, borderRadius: "8px", backgroundColor: "#353936" }}
      >
        {agentSupportsFileUploads && (
          <InputLeftAddon
            sx={{
              backgroundColor: "transparent",
              border: "none",
              color: "#59F886",
              cursor: "pointer",
            }}
            onClick={() =>
              document.querySelector('input[type="file"]')?.click()
            }
          >
            <input
              style={{ display: "none" }}
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <AttachmentIcon
              sx={{ color: file !== null ? "#6C6C6C" : "inherit" }}
            />
          </InputLeftAddon>
        )}
        <Input
          onKeyDown={(e) => {
            if (disabled) return;
            if (e.altKey && e.key === "Enter") {
              setMessage(message + "\n");
            } else if (e.key === "Enter") {
              handleSubmit();
            }
          }}
          sx={{
            border: "none",
            color: "white",
            "&:focus": {
              borderColor: "none !important",
              boxShadow: "none !important",
            },
          }}
          disabled={disabled || file !== null}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
        />
        <InputRightAddon
          sx={{ backgroundColor: "transparent", border: "none" }}
        >
          <IconButton
            sx={{
              backgroundColor: "transparent",
              fontSize: "24px",
              color: "#59F886",
              "&:hover": { backgroundColor: "transparent" },
            }}
            disabled={disabled}
            aria-label="Send"
            onClick={handleSubmit}
            icon={<SendIcon width="24px" height="24px" />}
          />
        </InputRightAddon>
      </InputGroup>
    </Flex>
  );
};
