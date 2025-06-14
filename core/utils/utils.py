from colorama import Fore, init
from web3 import Web3
from ..config import GTE_TOKENS, BASE_TOKEN, ERC20_ABI

init(autoreset=True)

def print_header():
    banner = f"""{Fore.CYAN}
    ███╗   ███╗███████╗ ██████╗  █████╗ ████████╗██╗  ██╗
    ████╗ ████║██╔════╝██╔════╝ ██╔══██╗╚══██╔══╝██║  ██║
    ██╔████╔██║█████╗  ██║  ███╗███████║   ██║   ███████║
    ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║   ██║   ██╔══██║
    ██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║   ██║   ██║  ██║
    ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
    {Fore.YELLOW}Multi-Wallet Version | {Fore.GREEN}Explorer: megaexplorer.xyz
    """
    print(banner)
    print(Fore.WHITE + "="*60)
    print(Fore.CYAN + "📌 Fitur Baru:")
    print(Fore.YELLOW + "✅ Multi-Wallet Support")
    print(Fore.YELLOW + "✅ Link Explorer Transaksi")
    print(Fore.YELLOW + "✅ Laporan Statistik Detail")
    print(Fore.WHITE + "="*60 + "\n")

def get_private_keys():
    """Membaca multiple private keys dari file wallets.txt"""
    try:
        with open('wallets.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}❌ File wallets.txt tidak ditemukan")
        exit()

def get_token_balance(web3, account, symbol):
    data = GTE_TOKENS[symbol]
    if symbol == BASE_TOKEN:
        balance = web3.eth.get_balance(account.address)
    else:
        contract = web3.eth.contract(address=Web3.to_checksum_address(data["address"]), abi=ERC20_ABI)
        balance = contract.functions.balanceOf(account.address).call()
    return balance / (10 ** data["decimals"])

def show_balances(web3, account):
    print(f"\n{Fore.CYAN}💰 SALDO WALLET {account.address}")
    max_length = max(len(symbol) for symbol in GTE_TOKENS)
    for symbol in GTE_TOKENS:
        amount = get_token_balance(web3, account, symbol)
        color = Fore.GREEN if amount > 0 else Fore.RED
        print(f"{Fore.YELLOW}{symbol.ljust(max_length)}: {color}{amount:.6f}")
    print()
