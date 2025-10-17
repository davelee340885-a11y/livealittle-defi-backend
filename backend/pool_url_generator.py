"""
池外部連結生成器 V4 - 最終版
現實情況: DefiLlama API 大部分池沒有提供 pool_address
解決方案: 優先使用協議概覽頁面,讓用戶自己找池(最實際的方案)
"""

def generate_pool_url(pool_id: str, protocol: str, chain: str, symbol: str = "", pool_address: str = "") -> str:
    """
    生成池的外部連結
    
    策略(V4 - 最終版):
    1. 如果有 pool_address,生成協議直連(理想情況,但很少見)
    2. 如果沒有 pool_address,返回協議的 LP 概覽頁面(實際情況)
    3. 最後後備使用 DefiLlama
    
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
    
    # ===== 策略 1: 如果有 pool_address,生成協議直連 =====
    # (理想情況,但 DefiLlama 很少提供)
    if pool_address and pool_address.startswith('0x') and len(pool_address) >= 42:
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
    # Raydium
    if 'raydium' in protocol_lower and pool_id:
        return f"https://raydium.io/liquidity/increase/?pool_id={pool_id}"
    
    # Orca
    if 'orca' in protocol_lower and pool_id:
        return f"https://www.orca.so/pools?pool={pool_id}"
    
    # ===== 策略 3: 協議 LP 概覽頁面(主要策略) =====
    # 現實情況: DefiLlama 大部分池沒有 pool_address
    # 解決方案: 返回協議的 LP 概覽頁面,讓用戶自己找池
    
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
    
    # Curve
    if 'curve' in protocol_lower:
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
        return f"https://app.balancer.fi/#/{chain_param}/pools"
    
    # SushiSwap
    if 'sushi' in protocol_lower:
        return "https://www.sushi.com/pool"
    
    # TraderJoe
    if 'traderjoe' in protocol_lower or 'trader-joe' in protocol_lower:
        return "https://traderjoexyz.com/avalanche/pool"
    
    # ===== 策略 4: DefiLlama 池頁面(最後後備) =====
    if pool_id and len(pool_id) > 10:
        return f"https://defillama.com/yields/pool/{pool_id}"
    
    # 最後的最後: DefiLlama 總覽
    return "https://defillama.com/yields"


def generate_protocol_direct_link(protocol: str, chain: str) -> str:
    """
    生成協議的直接連結(用於前端的「在協議上查看」按鈕)
    與 generate_pool_url 的策略 3 相同
    
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
    
    # Curve
    if 'curve' in protocol_lower:
        return "https://curve.fi"
    
    # Balancer
    if 'balancer' in protocol_lower:
        return "https://app.balancer.fi"
    
    # SushiSwap
    if 'sushi' in protocol_lower:
        return "https://www.sushi.com"
    
    # TraderJoe
    if 'traderjoe' in protocol_lower or 'trader-joe' in protocol_lower:
        return "https://traderjoexyz.com"
    
    return "https://defillama.com/yields"


# 測試
if __name__ == "__main__":
    test_cases = [
        {
            "name": "Uniswap V3 - 有 pool_address(罕見)",
            "pool_id": "bbecbf69-a4f7-43e3-8b72-de180d106e2c",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WBTC-USDC",
            "pool_address": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35"
        },
        {
            "name": "Uniswap V3 - 無 pool_address(常見)",
            "pool_id": "fc9f488e-8183-416f-a61e-4e5c571d4395",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WETH-USDT",
            "pool_address": ""
        },
        {
            "name": "Uniswap V3 - Arbitrum",
            "pool_id": "some-uuid",
            "protocol": "uniswap-v3",
            "chain": "Arbitrum",
            "symbol": "WETH-USDC",
            "pool_address": ""
        },
        {
            "name": "Raydium - Solana",
            "pool_id": "f3fa7ee4-bd8e-4ded-820f-4e775954b240",
            "protocol": "raydium-amm",
            "chain": "Solana",
            "symbol": "USDC-LINK",
            "pool_address": ""
        },
    ]
    
    print("=== 池 URL 生成測試(V4 - 最終版,協議概覽優先) ===\n")
    for case in test_cases:
        print(f"測試: {case['name']}")
        print(f"協議: {case['protocol']}")
        print(f"鏈: {case['chain']}")
        print(f"pool_address: {case['pool_address'] or '(無)'}")
        
        url = generate_pool_url(
            pool_id=case['pool_id'],
            protocol=case['protocol'],
            chain=case['chain'],
            symbol=case['symbol'],
            pool_address=case['pool_address']
        )
        
        print(f"✅ 池連結: {url}")
        
        # 判斷連結類型
        if case['pool_address'] and '0x' in url:
            print(f"   類型: 協議直連(包含池地址)")
        elif 'defillama' in url:
            print(f"   類型: DefiLlama 後備")
        else:
            print(f"   類型: 協議 LP 概覽頁面")
        
        print()

