export const routerAddress = "0x111111125421cA6dc452d289314280a0f8842A65";
export const oneInchNativeToken = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE";

export const availableAgents: {
  [key: string]: {
    name: string;
    description: string;
    endpoint: string;
    requirements: {
      connectedWallet: boolean;
    };
    supportsFiles?: boolean;
  };
} = {
  "swap-agent": {
    name: "Morpheus",
    description:
      "performs multiple tasks crypto data agent,swap agent and rag agent",
    endpoint: "http://127.0.0.1:8888",
    requirements: {
      connectedWallet: true,
    },
    supportsFiles: true,
  },
};

const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "http://52.8.32.222:8888"
    : "http://localhost:8888";

export default API_BASE_URL;
