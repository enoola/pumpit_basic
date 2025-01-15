"""
PumpPortal WebSocket Client
This script connects to PumpPortal's WebSocket API to:
1. Listen for new token creation events
2. On first token detection, switch to monitoring that token's trades
3. Display trade updates every 500ms
New Coin Created: {'signature': '3ocJaro35UcoKFb5SmgtRMoV5WJsbDqikX6SuuacksWuVDwpW2adBM2CNozs11idoEc1AuMpSnzZAayptvyRm7ES', 
'mint': 'CcdRF4iiDogw8vDNwsZc8FPzXzEfoEfPfBPvGJBupump', 
'traderPublicKey': '6iTiknZqQup6YqVY1rPjTpKYtorVn6dsU8vrD3E1PadC', 
'txType': 'create', 
'initialBuy': 34612903.225806, 
'solAmount': 1, 
'bondingCurveKey': 'F6dP8UPqngh5Y9QxEfXas4wDVX3EgnAigaVrCuMt8E7o', 
'vTokensInBondingCurve': 1038387096.774194, 
'vSolInBondingCurve': 30.999999999999986, 
'marketCapSol': 29.853991922957412, 
'name': 'FANG-TOON', 
'symbol': 'FANG-TOON', 
'uri': 'https://ipfs.io/ipfs/Qmf2tGUNodWjqbNZbyHscefjF7a7b2TAJnNA2sM55pQLyq', 
'pool': 'pump'}
wallet pub key: 4rH2gyTk26RFJcBVFmynGgtghvQ9iHWB2dGiA157KvKU
wallet priv key: 4dvuLndLR3aSzGdK8GTjCEosQVZEeKwMAogXFauDxPVbh7benAjKYNocWa6sfka8rXebW6LxvoPzQdoUbnBjpziE
api key: eh470w1patgpam2hd54nayhmct0k8w1qf1hncp236hk6cvvkf4upjp2g8554yrbrchwjpguqdxknec2ean83grkpdhtpyhae60wq4mbn6x3kjwa4ennk4ub8696mum1jb5570gjra4yku9gw5akvbdxb4pxuj9cr4cv2ccg894pewhqa1858rk65d6n4mk86n264yj26nvkuf8
"""

import asyncio
import json
import requests
import websockets


API_KEY = "eh470w1patgpam2hd54nayhmct0k8w1qf1hncp236hk6cvvkf4upjp2g8554yrbrchwjpguqdxknec2ean83grkpdhtpyhae60wq4mbn6x3kjwa4ennk4ub8696mum1jb5570gjra4yku9gw5akvbdxb4pxuj9cr4cv2ccg894pewhqa1858rk65d6n4mk86n264yj26nvkuf8"
PRIORITY_FEE = 0.009  # Default priority fee for faster transactions

async def buy_token(token_mint, amount_sol=0.01):
    try:
        response = requests.post(
            url=f"https://pumpportal.fun/api/trade?api-key={API_KEY}",
            data={
                "action": "buy",
                "mint": token_mint,
                "amount": amount_sol,
                "denominatedInSol": "true",  # Amount is in SOL
                "slippage": 1,  # 1% slippage for buying
                "priorityFee": PRIORITY_FEE,
                "pool": "pump"
            }
        )
        
        response_data = {"success": response.status_code == 200, "data": response.text}
        if response.status_code == 200:
            print(f"Buy transaction successful for {token_mint}")
            print(f"Response data: {str(response_data)}")
        else:
            print(f"Buy transaction failed: {response.text}")
            print(f"Response data: {str(response_data)}")
        return response_data
            
    except Exception as e:
        print(f"Error buying token: {str(e)}")
        return False

async def sell_token(token_mint):
    try:
        # First get token balance to sell all
        response = requests.post(
            url=f"https://pumpportal.fun/api/trade?api-key={API_KEY}",
            data={
                "action": "sell",
                "mint": token_mint,
                "amount": 1,  # Sell all tokens
                "denominatedInSol": "false",  # Amount is in tokens (100%)
                "slippage": 7,  # 7% slippage as requested
                "priorityFee": PRIORITY_FEE,
                "pool": "pump"
            }
        )
        
        response_data = {"success": response.status_code == 200, "data": response.text}
        if response.status_code == 200:
            print(f"Sell transaction successful for {token_mint}")
            print(f"Response data: {str(response_data)}")
        else:
            print(f"Sell transaction failed: {response.text}")
            print(f"Response data: {str(response_data)}")
        return response_data
            
    except Exception as e:
        print(f"Error selling token: {str(e)}")
        return False

async def monitor_token(websocket, token_address, should_sell=False):
    try:
        buy_events_count = 0
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                # Skip subscription messages
                if "message" in data:
                    continue
                    
                # Format: mint | txType | vTokensInBondingCurve | marketCapSol
                print(f"{data['mint']} | {data['traderPublicKey']} | {data['txType']} | {data['solAmount']:,.2f}| {data['vTokensInBondingCurve']:,.2f} | {data['marketCapSol']:.2f} SOL")
                
                # Count buy events if we're waiting to sell
                if should_sell and data['txType'] == 'buy':
                    buy_events_count += 1
                    print(f"Detected buy event {buy_events_count}/2")
                    
                    # After 2 buy events, sell everything
                    if buy_events_count >= 2:
                        print("2 buy events detected, selling tokens...")
                        await sell_token(token_address)
                        return  # Exit monitoring after selling
                        
                await asyncio.sleep(0.5)  # 500ms interval
            except json.JSONDecodeError:
                print("Error decoding message:", message)
            except KeyError as e:
                print(f"Missing field in data: {e}")
    except Exception as e:
        print(f"Monitor error: {str(e)}")

async def subscribe():
    try:
        uri = "wss://pumpportal.fun/api/data"
        async with websockets.connect(uri) as websocket:
            # Subscribe to new token events
            payload = {
                "method": "subscribeNewToken",
            }
            await websocket.send(json.dumps(payload))
            
            # Skip subscription confirmation message
            message = await websocket.recv()
            print("Subscription status:", json.loads(message))
            
            print("Waiting for new token creation...")
            # Wait for actual token creation event
            async for message in websocket:
                data = json.loads(message)
                print("\nNew token detected:")
                print(json.dumps(data, indent=2))
                
                # Extract token address and subscribe to its trades
                token_address = data.get("mint")
                
                if token_address:
                    print(f"Attempting to buy {token_address}")
                    buy_response = await buy_token(token_address)
                    buy_success = buy_response["success"]
                if token_address:
                    # Unsubscribe from new token events
                    payload = {
                        "method": "unsubscribeNewToken",
                    }
                    await websocket.send(json.dumps(payload))
                    
                    # Subscribe to token trades
                    payload = {
                        "method": "subscribeTokenTrade",
                        "keys": [token_address]
                    }
                    await websocket.send(json.dumps(payload))
                    
                    print(f"\nNow monitoring trades for token: {token_address}")
                    # Monitor token trades and sell after 2 buy events if our buy was successful
                    await monitor_token(websocket, token_address, should_sell=buy_success)
                    break  # Exit after first token
                else:
                    print("No token address found in data, waiting for next event...")
                
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed unexpectedly")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


async def main():
    await subscribe()

if __name__ == "__main__":
    asyncio.run(main())
