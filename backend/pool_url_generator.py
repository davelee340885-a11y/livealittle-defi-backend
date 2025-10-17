"""
池外部連結生成器 V3
優先使用協議直連到 LP pool,參考 Krystal DeFi 的設計
讓用戶可以直接訪問池並添加流動性,而不是通過 DefiLlama 中轉
"""

def generate_pool_url(pool_id: str, protocol: str, chain: str, symbol: str = "", pool_address: str = "") -> str:
    """
    生成池的外部連結
    
    優先級（V3 - 協議直連優先）:
    1. 如果有 pool_address，優先生成協議直連（像 Krystal 一樣）
    2. 如果沒有 pool_address，使用 DefiLlama 池頁面作為後備
    3. 最後使用協議的流動性頁面
    
    Args:
        pool_id: 池 ID (DefiLlama UUID 格式)
        protocol: 協議名稱
        chain: 鏈名稱
        symbol: 池的交易對符號
        pool_address: 實際的池地址 (0x開頭，如果可用)
    
    Returns:
        外部連結 URL
    """
    protocol_lower = protocol.lower()
    chain_lower = chain.lower()
    
    # ===== 策略 1: 協議直連（優先）=====
    # 如果有 pool_address，直接生成協議鏈接
    # 這樣用戶可以直接訪問池並添加流動性
    if pool_address and pool_address.startswith('0x'):
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
            return f"https://app.uniswap.org/explore/pools/{chain_slug}/{pool_address}"
        
        # Aerodrome (Base)
        if 'aerodrome' in protocol_lower:
            return f"https://aerodrome.finance/liquidity/{pool_address}"
        
        # Pancakeswap
        if 'pancake' in protocol_lower:
            chain_map = {
                'bsc': 'bsc',
                'ethereum': 'eth',
                'arbitrum': 'arb'
            }
            chain_param = chain_map.get(chain_lower, 'bsc')
            return f"https://pancakeswap.finance/liquidity/{pool_address}?chain={chain_param}"
        
        # Curve
        if 'curve' in protocol_lower:
            return f"https://curve.fi/#/ethereum/pools/{pool_address}/deposit"
        
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
            return f"https://app.balancer.fi/#/{chain_param}/pool/{pool_address}"
        
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
            return f"https://www.sushi.com/pool/{chain_param}:{pool_address}"
    
    # ===== 策略 2: Solana 生態系統 =====
    # Solana 使用 pool_id 而不是地址
    # Raydium
    if 'raydium' in protocol_lower and pool_id:
        return f"https://raydium.io/liquidity/increase/?pool_id={pool_id}"
    
    # Orca
    if 'orca' in protocol_lower and pool_id:
        return f"https://www.orca.so/pools?pool={pool_id}"
    
    # ===== 策略 3: DefiLlama 池頁面（後備）=====
    # 如果沒有 pool_address，使用 DefiLlama 作為後備
    # DefiLlama 提供完整的池信息和跳轉按鈕
    if pool_id and len(pool_id) > 10:  # UUID 格式
        return f"https://defillama.com/yields/pool/{pool_id}"
    
    # ===== 策略 4: 協議流動性頁面（最後後備）=====
    protocol_liquidity_pages = {
        'uniswap': 'https://app.uniswap.org/explore/pools',
        'raydium': 'https://raydium.io/liquidity/',
        'orca': 'https://www.orca.so/pools',
        'aerodrome': 'https://aerodrome.finance/liquidity',
        'pancakeswap': 'https://pancakeswap.finance/liquidity',
        'curve': 'https://curve.fi/#/ethereum/pools',
        'balancer': 'https://app.balancer.fi/#/pools',
        'sushiswap': 'https://www.sushi.com/pool',
        'traderjoe': 'https://traderjoexyz.com/avalanche/pool'
    }
    
    for key, url in protocol_liquidity_pages.items():
        if key in protocol_lower:
            return url
    
    # 最後的後備: 返回 DefiLlama 總覽頁
    return "https://defillama.com/yields"


def generate_protocol_direct_link(protocol: str, chain: str) -> str:
    """
    生成協議的直接連結（用於前端的「在協議上查看」按鈕）
    
    Args:
        protocol: 協議名稱
        chain: 鏈名稱
    
    Returns:
        協議連結 URL
    """
    protocol_lower = protocol.lower()
    chain_lower = chain.lower()
    
    # Uniswap V3
    if 'uniswap' in protocol_lower:
        chain_map = {
            'ethereum': 'mainnet',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon',
            'base': 'base',
            'bnb': 'bnb',
            'celo': 'celo'
        }
        chain_slug = chain_map.get(chain_lower, 'mainnet')
        return f"https://app.uniswap.org/explore/pools/{chain_slug}"
    
    # Raydium
    if 'raydium' in protocol_lower:
        return "https://raydium.io/liquidity/"
    
    # Orca
    if 'orca' in protocol_lower:
        return "https://www.orca.so/pools"
    
    # Aerodrome
    if 'aerodrome' in protocol_lower:
        return "https://aerodrome.finance/liquidity"
    
    # Pancakeswap
    if 'pancake' in protocol_lower:
        chain_map = {
            'bsc': 'bsc',
            'ethereum': 'eth',
            'arbitrum': 'arb'
        }
        chain_param = chain_map.get(chain_lower, 'bsc')
        return f"https://pancakeswap.finance/liquidity?chain={chain_param}"
    
    # 默認返回協議首頁
    protocol_urls = {
        'curve': 'https://curve.fi',
        'balancer': 'https://app.balancer.fi',
        'sushiswap': 'https://www.sushi.com',
        'traderjoe': 'https://traderjoexyz.com'
    }
    
    for key, url in protocol_urls.items():
        if key in protocol_lower:
            return url
    
    return "https://defillama.com/yields"


# 測試
if __name__ == "__main__":
    test_cases = [
        {
            "name": "Uniswap V3 - 有 pool_address（應該直連協議）",
            "pool_id": "bbecbf69-a4f7-43e3-8b72-de180d106e2c",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WBTC-USDC",
            "pool_address": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35"
        },
        {
            "name": "Uniswap V3 - 無 pool_address（應該用 DefiLlama）",
            "pool_id": "fc9f488e-8183-416f-a61e-4e5c571d4395",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WETH-USDT",
            "pool_address": ""
        },
        {
            "name": "Raydium - Solana（應該用 pool_id）",
            "pool_id": "f3fa7ee4-bd8e-4ded-820f-4e775954b240",
            "protocol": "raydium-amm",
            "chain": "Solana",
            "symbol": "USDC-LINK",
            "pool_address": ""
        },
        {
            "name": "Aerodrome - Base（應該直連協議）",
            "pool_id": "some-uuid",
            "protocol": "aerodrome",
            "chain": "Base",
            "symbol": "WETH-USDC",
            "pool_address": "0xd0b53d9277642d899df5c87a3966a349a798f224"
        }
    ]
    
    print("=== 池 URL 生成測試（V3 - 協議直連優先，像 Krystal） ===\n")
    for case in test_cases:
        print(f"測試: {case['name']}")
        print(f"協議: {case['protocol']}")
        print(f"鏈: {case['chain']}")
        print(f"池: {case['symbol']}")
        print(f"pool_address: {case['pool_address'] or '(無)'}")
        
        url = generate_pool_url(
            pool_id=case['pool_id'],
            protocol=case['protocol'],
            chain=case['chain'],
            symbol=case['symbol'],
            pool_address=case['pool_address']
        )
        
        protocol_url = generate_protocol_direct_link(case['protocol'], case['chain'])
        
        print(f"✅ 池連結: {url}")
        print(f"   協議連結: {protocol_url}")
        
        # 驗證是否直連
        if case['pool_address'] and case['pool_address'].startswith('0x'):
            if 'defillama' in url:
                print(f"   ⚠️  警告: 有 pool_address 但仍使用 DefiLlama")
            else:
                print(f"   ✅ 正確: 直接連結到協議池")
        
        print()

