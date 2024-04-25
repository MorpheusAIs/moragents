
qa_pairs = [

    # {
    #     "qa_id": 1,
    #     "nlq": [
    #         "I'd like to send 5USDC to 0x0000000000000000000000000000000000000000 on arbitrum",
    #         "I'd like to transfer 5 USDC to address 0x0000000000000000000000000000000000000000 on the Arbitrum network."
    #         "I'm interested in sending 5 USDC to the address 0x00000000000000000000000000000000000000000 on Arbitrum.",
    #         "move 5 USDC to the address 0x0000000000000000000000000000000000000000 on the Arbitrum network.",
    #         "I'd like to transmit 5 USDC to the address 0x00000000000000000000000000000000000000000"
    #     ],
    #     "payload":
    #         {
    #             "jsonrpc": "2.0",
    #             "method": "eth_call",
    #             "params": [
    #                 {
    #                     "to": "0x0000000000000000000000000000000000000000",
    #                     "data": "5USDC"
    #                 }
    #             ],
    #         }
    # },
    {
        "qa_id": 2,
        "nlq": [
            "What is my wallet's ETH balance?",
            "Can you tell me my current ETH balance?",
            "I'd like to know my Ethereum wallet balance, please.",
            "What's my balance in ETH?",
            "Can you check my Ethereum balance for me?"
        ],
        "payload":
            {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [
                    {
                        "address": "YOUR_WALLET_ADDRESS"
                    }
                ]
            }
    },
    {
        "qa_id": 3,
        "nlq": [
            "What was my last transaction?",
            "What was my most recent transaction?",
            "Can you tell me about my last transaction?",
            "What was my last transaction, and when did it occur?",
            "Can you provide details about my last transaction for me?",
        ],
        "payload":
            {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [
                    {
                        "fromBlock": "latest"
                    }
                ],
            }
    },

]