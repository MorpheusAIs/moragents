from web3 import Web3

# Initialize Web3
web3 = Web3(Web3.HTTPProvider('YOUR_PROVIDER_URL'))

# Define the recipient's address and the amount to transfer
recipient_address = '0x0000000000000000000000000000000000000000'
amount = 5000000  # 5 USDC, assuming 6 decimal places

# Generate the method signature for the transfer function
transfer_method_signature = web3.keccak(text='transfer(address,uint256)').hex()[:10]

# Prepare the parameters for the data field
# Note: The parameters need to be ABI encoded. For simplicity, let's manually construct the data field for demonstration.
recipient_address_padded = recipient_address[2:].rjust(64, '0')  # Remove '0x' and pad
amount_padded = hex(amount)[2:].rjust(64, '0')  # Convert to hex, remove '0x', and pad

# Construct the data field
transfer_data = transfer_method_signature + recipient_address_padded + amount_padded

# Example transaction
transaction = {
    'to': '0xContractAddressForUSDCOnArbitrum',  # USDC contract address
    'data': transfer_data,
    'gas': 200000,
    'gasPrice': web3.to_wei('5', 'gwei'),
}


# Payload would contain a chain_id field to specify which blockchain

print(transaction)
