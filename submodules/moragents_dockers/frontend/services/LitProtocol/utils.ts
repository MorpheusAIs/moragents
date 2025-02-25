import { WebUploader } from "@irys/web-upload";
import { WebEthereum } from "@irys/web-upload-ethereum";
import { EthersV6Adapter } from "@irys/web-upload-ethereum-ethers-v6";
import { ethers } from "ethers";
import { LitNodeClient } from "@lit-protocol/lit-node-client";
import { encryptString, decryptToString } from "@lit-protocol/encryption";
import { LIT_NETWORK, LIT_ABILITY } from "@lit-protocol/constants";
import {
  LitAccessControlConditionResource,
  createSiweMessage,
  generateAuthSig,
} from "@lit-protocol/auth-helpers";

const gatewayAddress = "https://gateway.irys.xyz/";

const getIrysUploader = async () => {
  const provider = new ethers.BrowserProvider(window.ethereum);
  const irysUploader = await WebUploader(WebEthereum).withAdapter(
    EthersV6Adapter(provider)
  );
  return irysUploader;
};

const litClient = new LitNodeClient({
  litNetwork: LIT_NETWORK.DatilDev,
});

const getAccessControlConditions = () => {
  return [
    {
      conditionType: "evmBasic" as const,
      contractAddress: "" as const,
      standardContractType: "" as const,
      chain: "ethereum" as const,
      method: "eth_getBalance" as const,
      parameters: [":userAddress", "latest"],
      returnValueTest: {
        comparator: ">=" as const,
        value: "10000000000000", // 0.00001 ETH
      },
    },
  ];
};

export const encryptSecret = async (
  text: string
): Promise<{ ciphertext: string; dataToEncryptHash: string }> => {
  await litClient.connect();

  const { ciphertext, dataToEncryptHash } = await encryptString(
    {
      accessControlConditions: getAccessControlConditions(),
      dataToEncrypt: text,
      chain: "ethereum",
    },
    litClient
  );

  return { ciphertext, dataToEncryptHash };
};

export const uploadToIrys = async (
  cipherText: string,
  dataToEncryptHash: string
): Promise<string> => {
  const irysUploader = await getIrysUploader();

  const dataToUpload = {
    ciphertext: cipherText, // Note: using ciphertext (lowercase) consistently
    dataToEncryptHash: dataToEncryptHash,
    accessControlConditions: getAccessControlConditions(),
  };

  try {
    const tags = [{ name: "Content-Type", value: "application/json" }];
    const receipt = await irysUploader.upload(JSON.stringify(dataToUpload), {
      tags,
    });
    return receipt?.id ? `${gatewayAddress}${receipt.id}` : "";
  } catch (error) {
    console.error("Error uploading data: ", error);
    throw error;
  }
};

export const downloadFromIrys = async (
  id: string
): Promise<[string, string, any[]]> => {
  const url = `${gatewayAddress}${id}`;
  console.log("Downloading from URL:", url);

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to retrieve data for ID: ${id}`);

    const data = await response.json();
    console.log("Raw data from Irys:", data);

    // Ensure consistent property names
    const ciphertext = data.ciphertext || data.cipherText;
    const dataToEncryptHash = data.dataToEncryptHash;
    const accessControlConditions = data.accessControlConditions;

    if (!ciphertext || !dataToEncryptHash || !accessControlConditions) {
      console.error("Missing required data from Irys:", {
        ciphertext,
        dataToEncryptHash,
        accessControlConditions,
      });
      throw new Error("Missing required data from Irys");
    }

    return [ciphertext, dataToEncryptHash, accessControlConditions];
  } catch (error) {
    console.error("Error retrieving data:", error);
    throw error;
  }
};

export const decryptData = async (
  encryptedText: string,
  dataToEncryptHash: string,
  accessControlConditions: any[]
): Promise<string> => {
  console.log("Decrypting with:", {
    encryptedText,
    dataToEncryptHash,
    accessControlConditions,
  });

  await litClient.connect();

  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  const walletAddress = await signer.getAddress();

  const latestBlockhash = await litClient.getLatestBlockhash();

  // Get session signatures
  const sessionSigs = await litClient.getSessionSigs({
    chain: "ethereum",
    expiration: new Date(Date.now() + 1000 * 60 * 10).toISOString(), // 10 minutes
    resourceAbilityRequests: [
      {
        resource: new LitAccessControlConditionResource("*"),
        ability: LIT_ABILITY.AccessControlConditionDecryption,
      },
    ],
    authNeededCallback: async ({
      uri,
      expiration,
      resourceAbilityRequests,
    }) => {
      const toSign = await createSiweMessage({
        uri,
        expiration,
        resources: resourceAbilityRequests,
        walletAddress: walletAddress,
        nonce: latestBlockhash,
        litNodeClient: litClient,
      });

      return await generateAuthSig({
        signer: signer,
        toSign,
      });
    },
  });

  // Decrypt using sessionSigs
  try {
    const decryptedString = await decryptToString(
      {
        accessControlConditions,
        chain: "ethereum",
        ciphertext: encryptedText,
        dataToEncryptHash,
        sessionSigs,
      },
      litClient
    );

    return decryptedString;
  } catch (error) {
    console.error("Decryption error:", error);
    throw error;
  }
};
