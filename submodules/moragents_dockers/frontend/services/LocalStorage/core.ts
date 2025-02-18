// src/services/localStorage/core.ts
import { LocalStorageData } from "@/services/types";
import {
  STORAGE_KEY,
  DEFAULT_MESSAGE,
  DEFAULT_CONVERSATION_ID,
} from "./config";

// Initialize local storage with default data
export const initializeStorage = (): LocalStorageData => {
  const defaultData: LocalStorageData = {
    conversations: {
      [DEFAULT_CONVERSATION_ID]: {
        id: DEFAULT_CONVERSATION_ID,
        messages: [DEFAULT_MESSAGE],
        createdAt: Date.now(),
        hasUploadedFile: false,
      },
    },
    lastConversationId: 0,
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
  return defaultData;
};

// Get all data from local storage
export const getStorageData = (): LocalStorageData => {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) {
    return initializeStorage();
  }

  try {
    const parsedData = JSON.parse(data) as LocalStorageData;

    return parsedData;
  } catch (error) {
    console.error("Error parsing chat data from localStorage:", error);
    return initializeStorage();
  }
};

// Save data to local storage
export const saveStorageData = (data: LocalStorageData): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};
