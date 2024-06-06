import axios, { Axios } from 'axios';
import { CANCELLED } from 'dns';
import { availableAgents } from '../config';

export type ChatMessageBase = {
    role: "user" | "assistant" | "swap";
};

export type UserOrAssistantMessage = ChatMessageBase & {
    role: "user" | "assistant";
    content: string;
};

export const SWAP_STATUS = {
    CANCELLED: "cancelled",
    SUCCESS: "success",
    FAIL: "failed",
    INIT: "initiated"
}

export type SwapTxPayloadType = {
    dstAmount: string;
    tx: {
        data: string;
        from: string;
        gas: number;
        gasPrice: string;
        to: string;
        value: string;
    };
};

export type ApproveTxPayloadType = {
    data: string;
    gasPrice: string;
    to: string;
    value: string;
};

export type SwapMessagePayload = {
    amount: string;
    dst: string;
    dst_address: string;
    dst_amount: string | number;
    quote: string;
    src: string;
    src_address: string;
    src_amount: string | number;
};

export type SwapMessage = ChatMessageBase & {
    role: "swap";
    content: SwapMessagePayload;
};

export type SystemMessage = ChatMessageBase & {
    role: "system";
    content: string;
};

export type ChatMessage = UserOrAssistantMessage | SwapMessage | SystemMessage;

export type ChatsListItem = {
    index: number; //  index at chats array
    title: string; // title of the chat (first message content)
}

export const getHttpClient = (selectedAgent: string) => {

    const agentData = availableAgents[selectedAgent];

    if (typeof agentData === 'undefined') {
        // if no agent selected lets select by default swap agent for now.
    }

    const swapAgentUrl = agentData?.endpoint || availableAgents['swap-agent'].endpoint;

    return axios.create({
        baseURL: swapAgentUrl || 'http://localhost:8080',
    });
}

export const getChats = async () => {
    // now chats will be stored at local storage

    const chats = localStorage.getItem('chats');
    if (chats) {
        return JSON.parse(chats);
    }

    return [];
}

//

export const getAllowance = async (backendClient: Axios, chainId: number, tokenAddress: string, walletAddress: string) => {
    return await backendClient.post('/allowance', {
        "chain_id": chainId,
        "tokenAddress": tokenAddress,
        "walletAddress": walletAddress
    });
}

export const getApprovalTxPayload = async (backendClient: Axios, chainId: number, tokenAddress: string, amount: number, decimals: number) => {
    return await backendClient.post('/approve', {
        "chain_id": chainId,
        "tokenAddress": tokenAddress,
        "amount": BigInt(amount * (10 ** decimals)).toString()
    });
}

export const uploadFile = async (backendClient: Axios, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return await backendClient.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
}

export const getSwapTxPayload = async (backendClient: Axios,
    token0: string,
    token1: string,
    walletAddress: string,
    amount: number,
    slippage: number,
    chainId: number,
    decimals: number,
): Promise<SwapTxPayloadType> => {
    return (await backendClient.post('/swap', {
        src: token0,
        dst: token1,
        walletAddress: walletAddress,
        amount: BigInt(amount * 10 ** decimals).toString(),
        slippage: slippage,
        chain_id: chainId
    })).data;
}

export const sendSwapStatus = async (
    backendClient: Axios,
    chainId: number,
    walletAddress: string,
    swapStatus: string,
    txHash?: string,
    swapType?: number
): Promise<ChatMessage> => {

    const responseBody = await backendClient.post('/tx_status', {
        "chain_id": chainId,
        "wallet_address": walletAddress,
        "status": swapStatus,
        "tx_hash": txHash || "",
        "tx_type": swapType === 0 ? "swap" : "approve", // 0 is swap, 1 is approve 
    });

    return {
        role: responseBody.data.role,
        content: responseBody.data.content
    } as ChatMessage;
}

export const getMessagesHistory = async (
    backendClient: Axios,
): Promise<ChatMessage[]> => {
    const responseBody = await backendClient.get('/messages');


    return responseBody.data.messages.map((message: any) => {
        return {
            role: message.role,
            content: message.content
        } as ChatMessage;

    });
}
export const writeMessage = async (
    history: ChatMessage[],
    message: string,
    backendClient: Axios,
    chainId: number,
    address: string
) => {
    const newMessage: ChatMessage = {
        role: 'user',
        content: message
    };

    history.push(newMessage);
    let resp;
    try {
        resp = await backendClient.post('/',
            {
                prompt: {
                    role: 'user',
                    content: message
                },
                "chain_id": String(chainId),
                "wallet_address": address,
            });
    } catch (e) {
        console.error(e);

        // resp = {
        //     data: {
        //         content: "Sorry, I'm not available right now. Please try again later."
        //     }
        // };
    } finally {
        console.log("Finally write message");
        // history.push({
        //     role: 'assistant',
        //     content: resp?.data.content || "Unknown error occurred."
        // });
    }

    return await getMessagesHistory(backendClient);
}