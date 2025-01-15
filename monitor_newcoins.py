import asyncio
import websockets
import json

# p python3 -m venv myenv
# source myvenv/bin/activate


async def monitor_new_coins():
    uri = "wss://pumpportal.fun/api/data"
    async with websockets.connect(uri) as websocket:
        # Subscribe to new token creation events
        subscription_message = json.dumps({
            "method": "subscribeNewToken"
        })
        await websocket.send(subscription_message)
        message = await websocket.recv()
        print("Subscribed to new token events.")
        message = await websocket.recv()
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                # Process and display the new token information
                print(f"New Coin Created: {data}")
                print(f"{data['solAmount']}")
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    asyncio.run(monitor_new_coins())

'''
""" New Coin Created: {'signature': '4mTsf1gW4HqmYHYjruA9prHFQZCWUXdjFG6H1uMES97bykUBSxd8Q2WQaGLHwfUwQ5vWpgohGJs1xPNUbAD3VUJW', 'mint': 'DtTGGfzoUJyq85kaLTxNEVqeuGXp3whXQC1xUivLpump', 'traderPublicKey': '4Cf1XZqzf7JU1NPbagBYXnLX4PWQCeA8gtFTbF3XTBcq', 'txType': 'create', 'initialBuy': 67062499.999999, 'solAmount': 2, 'bondingCurveKey': 'BQrUvKqZ4R18ztXkDxaaarAtDDacj6YG4ZNzCdYqpSvV', 'vTokensInBondingCurve': 1005937500.000001, 'vSolInBondingCurve': 31.999999999999968, 'marketCapSol': 31.811121466293816, 'name': 'First Red Note Chinese AI ', 'symbol': '工智慧', 'uri': 'https://ipfs.io/ipfs/QmYzaU88gbpvxcfP6w3F8dHTZUcv2qbGYMuZBxZKfYtJsj', 'pool': 'pump'} """
New Coin Created: {'signature': 'LQXUS4TSRCwwRo2XZCDenjnnhwSC2Uu1hYwGiUpDQZmcaqrLt2SwE4rCXbQwWzMCAnf8VVijV4Y879xLGr2AstP', 'mint': '4wf3veHTdGxo9ygMtdZndJVAJdgzh1HBUoV1niiqpump', 'traderPublicKey': '2bUj3CF1cE4QDsRuHJXns5DKmWGtGRAqNkKtbswMXCFc', 'txType': 'create', 'initialBuy': 17590163.934426, 'solAmount': 0.5, 'bondingCurveKey': '4k1csaV1uMxS9kxHeRbEtjb5wueRcV1zWgGckd9UkKVb', 'vTokensInBondingCurve': 1055409836.065574, 'vSolInBondingCurve': 30.499999999999993, 'marketCapSol': 28.8987263125194, 'name': 'Digger or N**ger ', 'symbol': 'Digger', 'uri': 'https://ipfs.io/ipfs/QmUDkGYR6UGU7s1TTRVgn4BseJzP776qYfKL579p53F5qL', 'pool': 'pump'}
'''