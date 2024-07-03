export const routerAddress = '0x111111125421cA6dc452d289314280a0f8842A65';
export const oneInchNativeToken = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';

export const availableAgents: {
    [key: string]: {
        name: string,
        description: string,
        endpoint: string,
        requirements: {
            connectedWallet: boolean
        },
        supportsFiles?: boolean

    }
} = {
    'swap-agent': {
        'name': 'Swap Agent',
        'description': 'Get quotes and perform swaps between tokens',
        'endpoint': 'http://127.0.0.1:8080/swap_agent',
        requirements: {
            connectedWallet: true
        }
    },
    'functional-data-agent': {
        'name': 'Data Agent',
        'description': 'Ask about price, market cap, FDV or TVL',
        'endpoint': 'http://127.0.0.1:8080/data_agent',
        requirements: {
            connectedWallet: false
        }
    },
    'rag-agent': {
        'name': 'PDF Agent',
        'description': 'Ask questions about an uploaded PDF file',
        'endpoint': 'http://127.0.0.1:8080/rag_agent',
        requirements: {
            connectedWallet: false
        },
        supportsFiles: true
    }
}