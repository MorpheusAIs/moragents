import axios from "axios";
import { getAvailableAgents } from "@/services/apiHooks";

export const BASE_URL = "http://localhost:8080";

export const getHttpClient = () => {
  return axios.create({
    baseURL: BASE_URL,
  });
};

export const initializeBackendClient = () => {
  const backendClient = axios.create({
    baseURL: BASE_URL,
  });

  getAvailableAgents(backendClient).catch((error) => {
    console.error("Failed to initialize available agents:", error);
  });

  return backendClient;
};

export const SWAP_STATUS = {
  CANCELLED: "cancelled",
  SUCCESS: "success",
  FAIL: "failed",
  INIT: "initiated",
};

export const CLAIM_STATUS = {
  SUCCESS: "success",
  FAIL: "failed",
  INIT: "initiated",
};
