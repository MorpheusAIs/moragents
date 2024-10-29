import React from "react";
import { Box } from "@chakra-ui/react";
import { Zap, Flame, Globe2, Trophy, LineChart, Paperclip } from "lucide-react";
import styles from "./PrefilledOptions.module.css";

type PrefilledOption = {
  title: string;
  icon: React.ReactNode;
  examples: Array<{
    text: string;
    agent: string;
  }>;
};

type PrefilledOptionsProps = {
  onSelect: (message: string) => void;
};

const prefilledOptions: PrefilledOption[] = [
  {
    title: "Sizzling Tweets 🌶️ No Content Moderation 😅",
    icon: <Flame size={20} />,
    examples: [
      { text: "Write a based tweet about Crypto and AI", agent: "tweet" },
    ],
  },
  {
    title: "Real-time Info 🕸️",
    icon: <Globe2 size={20} />,
    examples: [{ text: "Real-time info about Company XYZ", agent: "realtime" }],
  },
  {
    title: "Trending Crypto News",
    icon: <Zap size={20} />,
    examples: [{ text: "Latest news for USDC", agent: "crypto" }],
  },
  {
    title: "Check MOR rewards 🏆",
    icon: <Trophy size={20} />,
    examples: [{ text: "How many MOR rewards do I have?", agent: "rewards" }],
  },
  {
    title:
      "Fetch Price, Market Cap, and TVL of coins and tokens supported on CoinGecko 📈",
    icon: <LineChart size={20} />,
    examples: [
      { text: "What's the price of ETH?", agent: "price" },
      { text: "What's the market cap of BTC?", agent: "price" },
    ],
  },
  {
    title:
      "Upload a PDF with paperclip icon, then ask questions about the PDF 📄",
    icon: <Paperclip size={20} />,
    examples: [
      { text: "Can you give me a summary?", agent: "pdf" },
      { text: "What's the main point of the document?", agent: "pdf" },
    ],
  },
];

const PrefilledOptions: React.FC<PrefilledOptionsProps> = ({ onSelect }) => {
  return (
    <div className={styles.prefilledContainer}>
      <div className={styles.prefilledInner}>
        {prefilledOptions.map((section, index) => (
          <div key={index} className={styles.prefilledSection}>
            <div className={styles.sectionTitle}>
              <Box className={styles.sectionIcon}>{section.icon}</Box>
              {section.title}
            </div>
            <div className={styles.examplesList}>
              {section.examples.map((example, exampleIndex) => (
                <button
                  key={exampleIndex}
                  className={styles.exampleButton}
                  onClick={() => onSelect(example.text)}
                >
                  {example.text}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PrefilledOptions;
