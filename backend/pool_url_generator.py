"""
池外部連結生成器
根據協議和鏈生成正確的 LP 池 URL,直接連結到協議的池頁面
"""

def generate_pool_url(pool_id: str, protocol: str, chain: str, symbol: str = "", pool_address: str = "") -> str:
    """
    生成池的外部連結,直接連結到協議的池頁面
    
    Args:
        pool_id: 池 ID (DefiLlama 格式或地址)
        protocol: 協議名稱
        chain: 鏈名稱
        symbol: 池的交易對符號
        pool_address: 實際的池地址 (0x開頭,從 poolMeta 提取)
    
    Returns:
        外部連結 URL
    """
    protocol_lower = protocol.lower()
    chain_lower = chain.lower()
    
    # 優先使用 pool_address,其次使用 pool_id (如果是地址格式)
    address_to_use = pool_address if pool_address else (pool_id if pool_id and pool_id.startswith('0x') else "")
    
    # Uniswap V3
    if 'uniswap' in protocol_lower and 'v3' in protocol_lower:
        chain_map = {
            'ethereum': 'mainnet',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon',
            'base': 'base',
            'bnb': 'bnb',
            'celo': 'celo'
        }
        chain_slug = chain_map.get(chain_lower, chain_lower)
        if address_to_use:
            return f"https://app.uniswap.org/explore/pools/{chain_slug}/{address_to_use}"
        # 如果沒有地址,返回協議的池列表頁面
        return f"https://app.uniswap.org/explore/pools/{chain_slug}"
    
    # Raydium (Solana)
    if 'raydium' in protocol_lower:
        # Raydium 使用自己的 pool_id 格式
        if pool_id and not pool_id.startswith('0x'):
            return f"https://raydium.io/liquidity/increase/?pool_id={pool_id}"
        return "https://raydium.io/liquidity/"
    
    # Orca (Solana)
    if 'orca' in protocol_lower:
        if pool_id:
            return f"https://www.orca.so/pools?pool={pool_id}"
        return "https://www.orca.so/pools"
    
    # Aerodrome (Base)
    if 'aerodrome' in protocol_lower:
        if address_to_use:
            return f"https://aerodrome.finance/liquidity/{address_to_use}"
        return "https://aerodrome.finance/liquidity"
    
    # Pancakeswap
    if 'pancake' in protocol_lower:
        chain_map = {
            'bsc': 'bsc',
            'ethereum': 'eth',
            'arbitrum': 'arb'
        }
        chain_param = chain_map.get(chain_lower, 'bsc')
        
        if address_to_use:
            return f"https://pancakeswap.finance/liquidity/{address_to_use}?chain={chain_param}"
        return f"https://pancakeswap.finance/liquidity?chain={chain_param}"
    
    # Curve
    if 'curve' in protocol_lower:
        if address_to_use:
            return f"https://curve.fi/#/ethereum/pools/{address_to_use}/deposit"
        return "https://curve.fi/#/ethereum/pools"
    
    # Balancer
    if 'balancer' in protocol_lower:
        chain_map = {
            'ethereum': 'mainnet',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon',
            'gnosis': 'gnosis'
        }
        chain_param = chain_map.get(chain_lower, 'mainnet')
        
        if address_to_use:
            return f"https://app.balancer.fi/#/{chain_param}/pool/{address_to_use}"
        return f"https://app.balancer.fi/#/{chain_param}/pools"
    
    # Trader Joe (Avalanche)
    if 'joe' in protocol_lower or 'trader' in protocol_lower:
        if address_to_use:
            return f"https://traderjoexyz.com/avalanche/pool/v21/{address_to_use}"
        return "https://traderjoexyz.com/avalanche/pool"
    
    # SushiSwap
    if 'sushi' in protocol_lower:
        chain_map = {
            'ethereum': 'ethereum',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon',
            'avalanche': 'avalanche'
        }
        chain_param = chain_map.get(chain_lower, 'ethereum')
        
        if address_to_use:
            return f"https://www.sushi.com/pool/{chain_param}:{address_to_use}"
        return f"https://www.sushi.com/pool?chainId={chain_param}"
    
    # 默認: 如果有 pool_id,返回 DefiLlama 的池頁面
    # DefiLlama 頁面有直接到協議的操作按鈕
    if pool_id:
        return f"https://defillama.com/yields/pool/{pool_id}"
    
    # 最後的後備: 返回協議首頁
    protocol_urls = {
        'uniswap': 'https://app.uniswap.org',
        'raydium': 'https://raydium.io',
        'orca': 'https://www.orca.so',
        'aerodrome': 'https://aerodrome.finance',
        'pancakeswap': 'https://pancakeswap.finance',
        'curve': 'https://curve.fi',
        'balancer': 'https://app.balancer.fi',
        'sushiswap': 'https://www.sushi.com'
    }
    
    for key, url in protocol_urls.items():
        if key in protocol_lower:
            return url
    
    return "https://defillama.com/yields"


# 測試
if __name__ == "__main__":
    test_cases = [
        {
            "pool_id": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WETH-USDC",
            "pool_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
        },
        {
            "pool_id": "747c1d2a-dccc-4ffc-8f16-3f3a2f6e8e5d",
            "protocol": "uniswap-v3",
            "chain": "Arbitrum",
            "symbol": "WETH-USDT",
            "pool_address": "0x641c00a822e8b671738d32a431a4fb6074e5c79d"
        },
        {
            "pool_id": "raydium-wsol-usdc",
            "protocol": "raydium-amm",
            "chain": "Solana",
            "symbol": "WSOL-USDC",
            "pool_address": ""
        }
    ]
    
    print("=== 池 URL 生成測試 ===\n")
    for case in test_cases:
        url = generate_pool_url(**case)
        print(f"協議: {case['protocol']}")
        print(f"鏈: {case['chain']}")
        print(f"池: {case['symbol']}")
        print(f"pool_address: {case['pool_address']}")
        print(f"URL: {url}")
        print()

