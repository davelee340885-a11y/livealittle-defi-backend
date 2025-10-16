"""
池外部連結生成器
根據協議和鏈生成正確的 LP 池 URL
"""

def generate_pool_url(pool_id: str, protocol: str, chain: str, symbol: str = "") -> str:
    """
    生成池的外部連結
    
    Args:
        pool_id: 池 ID (DefiLlama 格式或地址)
        protocol: 協議名稱
        chain: 鏈名稱
        symbol: 池的交易對符號
    
    Returns:
        外部連結 URL
    """
    protocol_lower = protocol.lower()
    chain_lower = chain.lower()
    
    # 優先策略: 如果 pool_id 不是地址格式 (0x開頭),
    # 使用 DefiLlama 的池頁面,因為它有完整的數據和操作連結
    if pool_id and not pool_id.startswith('0x'):
        return f"https://defillama.com/yields/pool/{pool_id}"
    
    # Uniswap V3
    if 'uniswap' in protocol_lower and 'v3' in protocol_lower:
        chain_map = {
            'ethereum': 'mainnet',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon',
            'base': 'base',
            'celo': 'celo'
        }
        
        chain_param = chain_map.get(chain_lower, 'mainnet')
        
        # 如果 pool_id 看起來像地址 (0x開頭)
        if pool_id.startswith('0x'):
            return f"https://app.uniswap.org/explore/pools/{chain_param}/{pool_id}"
        else:
            # DefiLlama ID,返回協議首頁
            return f"https://app.uniswap.org/explore/pools/{chain_param}"
    
    # Raydium (Solana)
    if 'raydium' in protocol_lower:
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
        if pool_id.startswith('0x'):
            return f"https://aerodrome.finance/liquidity/{pool_id}"
        return "https://aerodrome.finance/liquidity"
    
    # Pancakeswap
    if 'pancake' in protocol_lower:
        chain_map = {
            'bsc': 'bsc',
            'ethereum': 'eth',
            'arbitrum': 'arb'
        }
        chain_param = chain_map.get(chain_lower, 'bsc')
        
        if pool_id.startswith('0x'):
            return f"https://pancakeswap.finance/liquidity/{pool_id}?chain={chain_param}"
        return f"https://pancakeswap.finance/liquidity?chain={chain_param}"
    
    # Curve
    if 'curve' in protocol_lower:
        if pool_id.startswith('0x'):
            return f"https://curve.fi/#/ethereum/pools/{pool_id}/deposit"
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
        
        if pool_id.startswith('0x'):
            return f"https://app.balancer.fi/#/{chain_param}/pool/{pool_id}"
        return f"https://app.balancer.fi/#/{chain_param}/pools"
    
    # Trader Joe (Avalanche)
    if 'joe' in protocol_lower or 'trader' in protocol_lower:
        if pool_id.startswith('0x'):
            return f"https://traderjoexyz.com/avalanche/pool/v21/{pool_id}"
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
        
        if pool_id.startswith('0x'):
            return f"https://www.sushi.com/pool/{chain_param}:{pool_id}"
        return f"https://www.sushi.com/pool?chainId={chain_param}"
    
    # 默認: 返回 DefiLlama 的池頁面
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
            "symbol": "WETH-USDC"
        },
        {
            "pool_id": "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
            "protocol": "uniswap-v3",
            "chain": "Arbitrum",
            "symbol": "WETH-USDC"
        },
        {
            "pool_id": "raydium-wsol-usdc",
            "protocol": "raydium-amm",
            "chain": "Solana",
            "symbol": "WSOL-USDC"
        },
        {
            "pool_id": "747c1d2a-dccc-4ffc-8f16-3f3a2f6e8e5d",
            "protocol": "uniswap-v3",
            "chain": "Arbitrum",
            "symbol": "WETH-USDT"
        }
    ]
    
    print("=== 池 URL 生成測試 ===\n")
    for case in test_cases:
        url = generate_pool_url(**case)
        print(f"協議: {case['protocol']}")
        print(f"鏈: {case['chain']}")
        print(f"池: {case['symbol']}")
        print(f"URL: {url}")
        print()

