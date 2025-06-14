import time
import random
from web3 import Web3
from ..config import GTE_TOKENS, BASE_TOKEN, ROUTER_ADDRESS, ERC20_ABI, ROUTER_ABI, SLIPPAGE, GAS_MULTIPLIER

def approve(web3, account, token_address, amount):
    contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    tx = contract.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 100000,
        'gasPrice': int(web3.eth.gas_price * GAS_MULTIPLIER)
    })
    signed = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def swap(web3, account, router, token_in, token_out, amount_decimal):
    token_in_data = GTE_TOKENS[token_in]
    token_out_data = GTE_TOKENS[token_out]
    deadline = int(time.time()) + 1800
    amount_in = int(amount_decimal * (10 ** token_in_data["decimals"]))
    amount_out_min = 0
    tx_hash = None
    
    max_retries = 3
    for retry_count in range(max_retries):
        try:
            nonce = web3.eth.get_transaction_count(account.address, 'pending')
            
            # Handle different swap types
            if token_in == BASE_TOKEN:
                path = [GTE_TOKENS["WETH"]["address"], token_out_data["address"]]
                tx = router.functions.swapExactETHForTokens(
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'value': amount_in,
                    'gas': 300000,
                    'gasPrice': int(web3.eth.gas_price * GAS_MULTIPLIER),
                    'nonce': nonce
                })
            elif token_out == BASE_TOKEN:
                approve_hash = approve(web3, account, token_in_data["address"], amount_in)
                path = [token_in_data["address"], GTE_TOKENS["WETH"]["address"]]
                tx = router.functions.swapExactTokensForETH(
                    amount_in,
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'gas': 300000,
                    'gasPrice': int(web3.eth.gas_price * GAS_MULTIPLIER),
                    'nonce': nonce
                })
            else:
                approve_hash = approve(web3, account, token_in_data["address"], amount_in)
                path = [
                    token_in_data["address"],
                    GTE_TOKENS["WETH"]["address"],
                    token_out_data["address"]
                ]
                tx = router.functions.swapExactTokensForTokens(
                    amount_in,
                    amount_out_min,
                    path,
                    account.address,
                    deadline
                ).build_transaction({
                    'from': account.address,
                    'gas': 300000,
                    'gasPrice': int(web3.eth.gas_price * GAS_MULTIPLIER),
                    'nonce': nonce
                })

            signed = account.sign_transaction(tx)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"✅ SWAP {token_in} → {token_out} BERHASIL")
            return tx_hash.hex()
            
        except Exception as e:
            error_msg = str(e).lower()
            if "nonce too low" in error_msg or "already known" in error_msg:
                print(f"⚠️ Mencoba ulang transaksi ({retry_count+1}/{max_retries})")
                time.sleep(random.uniform(2, 5))
                continue
            print(f"❌ ERROR: {str(e)}")
            raise
    
    print("⛔ Gagal setelah 3x percobaan")
    return None
