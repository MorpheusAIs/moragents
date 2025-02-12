import {
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Box,
  Text,
  Flex,
  Divider,
} from "@chakra-ui/react";
import {
  IconDotsVertical,
  IconBrandDiscord,
  IconBrandTwitter,
  IconBrandGithub,
  IconQuestionMark,
  IconWorld,
} from "@tabler/icons-react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Workflows } from "@/components/Workflows";
import { ApiCredentialsButton } from "@/components/Credentials/Button";
import { CDPWalletsButton } from "@/components/CDPWallets/Button";
import { SettingsButton } from "@/components/Settings";
import styles from "./ProfileMenu.module.css";

const MenuSection = ({ title, children }) => (
  <Box mb={4}>
    <Text
      color="gray.400"
      fontSize="sm"
      px={3}
      py={2}
      textTransform="uppercase"
    >
      {title}
    </Text>
    {children}
  </Box>
);

const ExternalLinkMenuItem = ({ icon: Icon, title, href }) => (
  <MenuItem
    className={styles.externalMenuItem}
    onClick={() => window.open(href, "_blank", "noopener,noreferrer")}
  >
    <Flex align="center" gap={3}>
      {Icon && <Icon size={20} />}
      <Text>{title}</Text>
    </Flex>
  </MenuItem>
);

export const ProfileMenu = () => {
  return (
    <Menu>
      <MenuButton as={Box} className={styles.profileButton} width="100%">
        <ConnectButton.Custom>
          {({
            account,
            chain,
            openAccountModal,
            openChainModal,
            openConnectModal,
            mounted,
          }) => {
            const ready = mounted;
            const connected = ready && account && chain;

            return (
              <div
                {...(!ready && {
                  "aria-hidden": true,
                  style: {
                    opacity: 0,
                    pointerEvents: "none",
                    userSelect: "none",
                  },
                })}
                className={styles.connectButtonWrapper}
              >
                <div className={styles.profileContainer}>
                  <div
                    className={styles.accountInfo}
                    onClick={connected ? openAccountModal : openConnectModal}
                  >
                    {connected
                      ? "Active session logged in as " + account.displayName
                      : "Connect Wallet"}
                  </div>
                  <IconDotsVertical size={16} className={styles.menuIcon} />
                </div>
              </div>
            );
          }}
        </ConnectButton.Custom>
      </MenuButton>

      <MenuList className={styles.profileMenu}>
        <MenuSection title="Basic">
          <MenuItem className={styles.menuItem}>
            <SettingsButton />
          </MenuItem>
        </MenuSection>

        <Divider my={2} borderColor="whiteAlpha.200" />

        <MenuSection title="Advanced">
          <MenuItem className={styles.menuItem}>
            <Workflows />
          </MenuItem>
          <MenuItem className={styles.menuItem}>
            <ApiCredentialsButton />
          </MenuItem>
          <MenuItem className={styles.menuItem}>
            <CDPWalletsButton />
          </MenuItem>
        </MenuSection>

        <Divider my={2} borderColor="whiteAlpha.200" />

        <MenuSection title="About">
          <ExternalLinkMenuItem
            icon={IconBrandDiscord}
            title="Join our Discord community!"
            href="https://discord.gg/Dc26EFb6JK"
          />
          <ExternalLinkMenuItem
            icon={IconBrandTwitter}
            title="Follow us on Twitter"
            href="https://twitter.com/MorpheusAIs"
          />
          <ExternalLinkMenuItem
            icon={IconBrandGithub}
            title="Become a contributor"
            href="https://github.com/MorpheusAIs/Docs"
          />
          <ExternalLinkMenuItem
            icon={IconWorld}
            title="Learn about Morpheus"
            href="https://mor.org/"
          />
          <ExternalLinkMenuItem
            icon={IconQuestionMark}
            title="Help Center & FAQs"
            href="https://morpheusai.gitbook.io/morpheus/faqs"
          />
        </MenuSection>
      </MenuList>
    </Menu>
  );
};
