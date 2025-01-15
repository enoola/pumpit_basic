import asyncio
import websockets
import json
import csv
from datetime import datetime


"""
Aim : display and log in a CSV "pumpit_YYYYMMDD:hh:mm:ss.csv" realtime token and trades associated with it
   each line will represent a token event : creation/buy/sell
    #print(f"{data['mint']}  | {data['traderPublicKey']}| {data['solAmount']:,.2f} | {data['txType']} | {data['vTokensInBondingCurve']:,.2f} | {data['marketCapSol']:.2f} SOL"
"""

def get_creation_csv_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"pumpit_{timestamp}.csv"

def write_creation_to_csv(filename, data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            data['mint'],
            f"{data.get('solAmount', 0):.2f}",
            f"{data.get('vTokensInBondingCurve', 0):.2f}",
            f"{data.get('marketCapSol', 0):.2f}"
        ])

def write_transaction_to_csv(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = data.get("mint")+"_transaction.csv"
    
    # Create file with headers if it doesn't exist
    try:
        with open(filename, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Mint', 'Trader Public Key', 'SOL Amount', 'Transaction Type', 'Tokens In Bonding Curve', 'Market Cap SOL'])
    except FileExistsError:
        pass
        
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            data['mint'],
            data.get('traderPublicKey', 'N/A'),
            f"{data.get('solAmount', 0):.2f}",
            data.get('txType', 'TRADE'),
            f"{data.get('vTokensInBondingCurve', 0):.2f}",
            f"{data.get('marketCapSol', 0):.2f}"
        ])

async def monitor_token(websocket, token_address):
    try:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                # Skip subscription messages
                if "message" in data:
                    continue
                # Format: mint | txType | vTokensInBondingCurve | marketCapSol
                print(f"{data['mint']} | {data['traderPublicKey']} | {data['txType']} | {data['solAmount']:,.2f}| {data['vTokensInBondingCurve']:,.2f} | {data['marketCapSol']:.2f} SOL")
                write_transaction_to_csv(data)
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
        creation_csv = get_creation_csv_filename()
        
        # Initialize creation CSV file with headers
        with open(creation_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Mint', 'SOL Amount', 'Tokens In Bonding Curve', 'Market Cap SOL'])
        
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
                
                # Log token creation event
                write_creation_to_csv(creation_csv, data)
                
                # Extract token address and subscribe to its trades
                token_address = data.get("mint")
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
                    # Monitor token trades
                    await monitor_token(websocket=websocket, token_address=token_address)
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
