import React, { FC, useState } from "react";
import {
  Flex,
  Textarea,
  InputGroup,
  InputLeftAddon,
  InputRightAddon,
  IconButton,
} from "@chakra-ui/react";
import { AttachmentIcon } from "@chakra-ui/icons";
import { SendIcon } from "../CustomIcon/SendIcon";
import PrefilledOptions from "./PrefilledOptions";
import styles from "./index.module.css";

type ChatInputProps = {
  onSubmit: (message: string, file: File | null) => Promise<void>;
  disabled: boolean;
  hasMessages?: boolean;
};

export const ChatInput: FC<ChatInputProps> = ({
  onSubmit,
  disabled,
  hasMessages = false,
}) => {
  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const agentSupportsFileUploads = true;

  const handleSubmit = async () => {
    if (!message && !file) return;
    await onSubmit(message, file);
    setMessage("");
    setFile(null);
  };

  const handlePrefilledSelect = async (selectedMessage: string) => {
    await onSubmit(selectedMessage, null);
  };

  return (
    <>
      {!hasMessages && <PrefilledOptions onSelect={handlePrefilledSelect} />}
      <div className={styles.container}>
        <Flex className={styles.flexContainer}>
          <InputGroup className={styles.inputGroup}>
            {agentSupportsFileUploads && (
              <InputLeftAddon className={styles.fileAddon}>
                <input
                  type="file"
                  className={styles.hiddenInput}
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <IconButton
                  aria-label="Attach file"
                  icon={<AttachmentIcon />}
                  className={disabled ? styles.disabledIcon : ""}
                  disabled={disabled}
                  onClick={() =>
                    document
                      .querySelector('input[type="file"]')
                      ?.dispatchEvent(new MouseEvent("click"))
                  }
                />
              </InputLeftAddon>
            )}
            <Textarea
              className={styles.messageInput}
              onKeyDown={(e) => {
                if (disabled) return;
                if (e.altKey && e.key === "Enter") {
                  setMessage(message + "\n");
                } else if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              disabled={disabled || file !== null}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              rows={1}
              resize="none"
              overflow="hidden"
              minHeight="unset"
            />
            <InputRightAddon className={styles.rightAddon}>
              <IconButton
                className={styles.sendButton}
                disabled={disabled}
                aria-label="Send"
                onClick={handleSubmit}
                icon={<SendIcon width="24px" height="24px" />}
              />
            </InputRightAddon>
          </InputGroup>
        </Flex>
      </div>
    </>
  );
};
