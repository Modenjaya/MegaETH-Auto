import time
import random
from web3 import Web3
from eth_account import Account
from core.config import RPC_URL, ROUTER_ADDRESS, ROUTER_ABI, BASE_TOKEN, GTE_TOKENS
from core.utils.utils import print_header, get_private_keys, show_balances, get_token_balance
from core.swap.swap import swap

def process_wallet(private_key, rounds, swap_percent):
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = Account.from_key(private_key)
    router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)
    success_count = 0
    
    print(f"\n{Account.from_key(private_key).address}")
    show_balances(web3, account)

    swap_fraction = swap_percent / 100
    tokens = [k for k in GTE_TOKENS if k != BASE_TOKEN]

    for round_num in range(1, rounds+1):
        print(f"\n{Fore.CYAN}🔄 PUTARAN {round_num}/{rounds}")
        
        # Swap BASE -> GTE Tokens
        for token in tokens:
            balance = get_token_balance(web3, account, BASE_TOKEN)
            if balance > 0:
                amount = balance * swap_fraction
                print(f"\n{Fore.WHITE}🔀 Convert {BASE_TOKEN} -> {token}")
                tx_hash = swap(web3, account, router, BASE_TOKEN, token, amount)
                if tx_hash:
                    success_count += 1
                    print(f"{Fore.GREEN}🌐 Explorer: https://www.megaexplorer.xyz/tx/{tx_hash}")
                    time.sleep(random.uniform(3, 8))

        # Swap GTE Tokens -> BASE
        for token in tokens:
            balance = get_token_balance(web3, account, token)
            if balance > 0:
                print(f"\n{Fore.WHITE}🔀 Convert {token} -> {BASE_TOKEN}")
                tx_hash = swap(web3, account, router, token, BASE_TOKEN, balance)
                if tx_hash:
                    success_count += 1
                    print(f"{Fore.GREEN}🌐 Explorer: https://www.megaexplorer.xyz/tx/{tx_hash}")
                    time.sleep(random.uniform(3, 8))
    
    return success_count, account.address

def main():
    print_header()
    private_keys = get_private_keys()
    
    try:
        rounds = int(input(f"{Fore.YELLOW}🔁 Jumlah Putaran Swap: "))
        percent = float(input(f"{Fore.YELLOW}💸 Persen Swap per Transaksi (1-100): "))
    except ValueError:
        print(f"{Fore.RED}❌ Input tidak valid!")
        return

    if not 0 < percent <= 100:
        print(f"{Fore.RED}❌ Persen harus antara 1-100!")
        return

    total_success = 0
    results = []

    for idx, pk in enumerate(private_keys, 1):
        print(f"\n{Fore.CYAN}🚀 Memproses Wallet {idx}/{len(private_keys)}")
        try:
            success, address = process_wallet(pk, rounds, percent)
            total_success += success
            results.append((address, success))
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}")
            continue

    # Tampilkan laporan
    print(f"\n{Fore.CYAN}📊 LAPORAN AKHIR")
    print(f"{Fore.YELLOW}├{'─'*58}┤")
    print(f"{Fore.CYAN}│ {'Wallet Address':42} │ {'Success':^8} │")
    print(f"{Fore.YELLOW}├{'─'*42}┼{'─'*10}┤")
    for address, count in results:
        print(f"{Fore.WHITE}│ {address} │ {Fore.GREEN}{count:^8} {Fore.WHITE}│")
    print(f"{Fore.YELLOW}├{'─'*58}┤")
    print(f"{Fore.CYAN}│ Total Success: {Fore.GREEN}{total_success}{Fore.CYAN}{' ':43}│")
    print(f"{Fore.YELLOW}└{'─'*58}┘")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}⛔ Dibatalkan oleh pengguna")
