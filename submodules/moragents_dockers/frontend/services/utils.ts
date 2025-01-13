export const getHumanReadableAgentName = (agentName: string): string => {
  const agentNameMap: Record<string, string> = {
    default: "Morpheus AI",
    imagen: "Image Generator Agent",
    rag: "Document Analysis Agent",
    "crypto data": "Crypto Data Agent",
    "token swap": "Metamask Swaps Agent",
    "tweet sizzler": "Tweet Generator Agent",
    dca: "DCA Strategy Planning Agent",
    base: "Base Transactions Agent",
    "mor claims": "MOR Claims Agent",
    "mor rewards": "MOR Rewards Tracking Agent",
    "realtime search": "Real-Time Search Agent",
    "crypto news": "Crypto News Analysis Agent",
  };

  return agentNameMap[agentName] || agentName;
};
