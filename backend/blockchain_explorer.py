"""
區塊鏈瀏覽器鏈接生成器
生成各個區塊鏈的瀏覽器鏈接,用於驗證地址和交易
"""

class BlockchainExplorer:
    """區塊鏈瀏覽器鏈接生成器"""
    
    # 區塊鏈瀏覽器配置
    EXPLORERS = {
        'ethereum': {
            'name': 'Etherscan',
            'url': 'https://etherscan.io',
            'address': 'https://etherscan.io/address/{address}',
            'token': 'https://etherscan.io/token/{address}',
            'tx': 'https://etherscan.io/tx/{tx_hash}',
        },
        'arbitrum': {
            'name': 'Arbiscan',
            'url': 'https://arbiscan.io',
            'address': 'https://arbiscan.io/address/{address}',
            'token': 'https://arbiscan.io/token/{address}',
            'tx': 'https://arbiscan.io/tx/{tx_hash}',
        },
        'optimism': {
            'name': 'Optimistic Etherscan',
            'url': 'https://optimistic.etherscan.io',
            'address': 'https://optimistic.etherscan.io/address/{address}',
            'token': 'https://optimistic.etherscan.io/token/{address}',
            'tx': 'https://optimistic.etherscan.io/tx/{tx_hash}',
        },
        'polygon': {
            'name': 'Polygonscan',
            'url': 'https://polygonscan.com',
            'address': 'https://polygonscan.com/address/{address}',
            'token': 'https://polygonscan.com/token/{address}',
            'tx': 'https://polygonscan.com/tx/{tx_hash}',
        },
        'base': {
            'name': 'Basescan',
            'url': 'https://basescan.org',
            'address': 'https://basescan.org/address/{address}',
            'token': 'https://basescan.org/token/{address}',
            'tx': 'https://basescan.org/tx/{tx_hash}',
        },
        'bsc': {
            'name': 'BscScan',
            'url': 'https://bscscan.com',
            'address': 'https://bscscan.com/address/{address}',
            'token': 'https://bscscan.com/token/{address}',
            'tx': 'https://bscscan.com/tx/{tx_hash}',
        },
        'avalanche': {
            'name': 'Snowtrace',
            'url': 'https://snowtrace.io',
            'address': 'https://snowtrace.io/address/{address}',
            'token': 'https://snowtrace.io/token/{address}',
            'tx': 'https://snowtrace.io/tx/{tx_hash}',
        },
        'celo': {
            'name': 'Celoscan',
            'url': 'https://celoscan.io',
            'address': 'https://celoscan.io/address/{address}',
            'token': 'https://celoscan.io/token/{address}',
            'tx': 'https://celoscan.io/tx/{tx_hash}',
        },
        'gnosis': {
            'name': 'Gnosisscan',
            'url': 'https://gnosisscan.io',
            'address': 'https://gnosisscan.io/address/{address}',
            'token': 'https://gnosisscan.io/token/{address}',
            'tx': 'https://gnosisscan.io/tx/{tx_hash}',
        },
        'fantom': {
            'name': 'FTMScan',
            'url': 'https://ftmscan.com',
            'address': 'https://ftmscan.com/address/{address}',
            'token': 'https://ftmscan.com/token/{address}',
            'tx': 'https://ftmscan.com/tx/{tx_hash}',
        },
        'solana': {
            'name': 'Solscan',
            'url': 'https://solscan.io',
            'address': 'https://solscan.io/account/{address}',
            'token': 'https://solscan.io/token/{address}',
            'tx': 'https://solscan.io/tx/{tx_hash}',
        },
    }
    
    # Chain ID 映射
    CHAIN_IDS = {
        'ethereum': 1,
        'arbitrum': 42161,
        'optimism': 10,
        'polygon': 137,
        'base': 8453,
        'bsc': 56,
        'avalanche': 43114,
        'celo': 42220,
        'gnosis': 100,
        'fantom': 250,
    }
    
    def get_explorer_name(self, chain: str) -> str:
        """
        獲取區塊鏈瀏覽器名稱
        
        Args:
            chain: 區塊鏈名稱
            
        Returns:
            瀏覽器名稱
        """
        chain_lower = chain.lower()
        if chain_lower in self.EXPLORERS:
            return self.EXPLORERS[chain_lower]['name']
        return 'Explorer'
    
    def get_explorer_url(self, chain: str) -> str:
        """
        獲取區塊鏈瀏覽器首頁 URL
        
        Args:
            chain: 區塊鏈名稱
            
        Returns:
            瀏覽器首頁 URL
        """
        chain_lower = chain.lower()
        if chain_lower in self.EXPLORERS:
            return self.EXPLORERS[chain_lower]['url']
        return None
    
    def get_address_url(self, chain: str, address: str) -> str:
        """
        獲取地址瀏覽器 URL
        
        Args:
            chain: 區塊鏈名稱
            address: 合約或錢包地址
            
        Returns:
            地址瀏覽器 URL
        """
        chain_lower = chain.lower()
        if chain_lower in self.EXPLORERS:
            template = self.EXPLORERS[chain_lower]['address']
            return template.format(address=address)
        return None
    
    def get_token_url(self, chain: str, token_address: str) -> str:
        """
        獲取代幣瀏覽器 URL
        
        Args:
            chain: 區塊鏈名稱
            token_address: 代幣合約地址
            
        Returns:
            代幣瀏覽器 URL
        """
        chain_lower = chain.lower()
        if chain_lower in self.EXPLORERS:
            template = self.EXPLORERS[chain_lower]['token']
            return template.format(address=token_address)
        return None
    
    def get_tx_url(self, chain: str, tx_hash: str) -> str:
        """
        獲取交易瀏覽器 URL
        
        Args:
            chain: 區塊鏈名稱
            tx_hash: 交易哈希
            
        Returns:
            交易瀏覽器 URL
        """
        chain_lower = chain.lower()
        if chain_lower in self.EXPLORERS:
            template = self.EXPLORERS[chain_lower]['tx']
            return template.format(tx_hash=tx_hash)
        return None
    
    def get_chain_id(self, chain: str) -> int:
        """
        獲取 Chain ID
        
        Args:
            chain: 區塊鏈名稱
            
        Returns:
            Chain ID,如果不支持返回 0
        """
        chain_lower = chain.lower()
        return self.CHAIN_IDS.get(chain_lower, 0)
    
    def is_valid_address(self, address: str, chain: str = 'ethereum') -> bool:
        """
        驗證地址格式是否有效
        
        Args:
            address: 地址字符串
            chain: 區塊鏈名稱
            
        Returns:
            是否為有效地址
        """
        if not address:
            return False
        
        chain_lower = chain.lower()
        
        # Solana 地址格式不同
        if chain_lower == 'solana':
            # Solana 地址通常是 32-44 字符的 base58 編碼
            return len(address) >= 32 and len(address) <= 44
        
        # EVM 鏈地址格式
        if isinstance(address, str):
            # 標準以太坊地址: 0x + 40 個十六進制字符
            if address.startswith('0x') and len(address) == 42:
                return True
            # Uniswap V3 等可能有更長的 pool ID
            if address.startswith('0x') and len(address) > 42:
                return True
        
        return False
    
    def generate_explorer_links(self, chain: str, pool_address: str = None, 
                               token0_address: str = None, token1_address: str = None) -> dict:
        """
        生成所有相關的瀏覽器鏈接
        
        Args:
            chain: 區塊鏈名稱
            pool_address: 池地址
            token0_address: 代幣0地址
            token1_address: 代幣1地址
            
        Returns:
            包含所有瀏覽器鏈接的字典
        """
        links = {
            'explorer_name': self.get_explorer_name(chain),
            'explorer_url': self.get_explorer_url(chain),
        }
        
        if pool_address and self.is_valid_address(pool_address, chain):
            links['pool_explorer_url'] = self.get_address_url(chain, pool_address)
        
        if token0_address and self.is_valid_address(token0_address, chain):
            links['token0_explorer_url'] = self.get_token_url(chain, token0_address)
        
        if token1_address and self.is_valid_address(token1_address, chain):
            links['token1_explorer_url'] = self.get_token_url(chain, token1_address)
        
        return links
    
    def generate_blockchain_info(self, chain: str) -> dict:
        """
        生成區塊鏈完整信息
        
        Args:
            chain: 區塊鏈名稱
            
        Returns:
            區塊鏈信息字典
        """
        return {
            'chain': chain,
            'chain_id': self.get_chain_id(chain),
            'explorer_name': self.get_explorer_name(chain),
            'explorer_url': self.get_explorer_url(chain),
        }


# 測試
if __name__ == "__main__":
    explorer = BlockchainExplorer()
    
    print("=== 區塊鏈瀏覽器鏈接生成測試 ===\n")
    
    # 測試案例
    test_cases = [
        {
            'chain': 'ethereum',
            'pool_address': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
            'token0_address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
            'token1_address': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        },
        {
            'chain': 'arbitrum',
            'pool_address': '0xc31e54c7a869b9fcbecc14363cf510d1c41fa443',
        },
        {
            'chain': 'base',
            'pool_address': '0xd0b53d9277642d899df5c87a3966a349a798f224',
        },
    ]
    
    for case in test_cases:
        print(f"區塊鏈: {case['chain']}")
        print(f"瀏覽器: {explorer.get_explorer_name(case['chain'])}")
        print(f"Chain ID: {explorer.get_chain_id(case['chain'])}")
        
        if 'pool_address' in case:
            print(f"池地址: {explorer.get_address_url(case['chain'], case['pool_address'])}")
        
        if 'token0_address' in case:
            print(f"代幣0: {explorer.get_token_url(case['chain'], case['token0_address'])}")
        
        if 'token1_address' in case:
            print(f"代幣1: {explorer.get_token_url(case['chain'], case['token1_address'])}")
        
        print()

