import requests
import json

TOKEN = '8431658256:AAFpuYSGZf8LklVtGJgxO1_n9buXzkDPXwc'
base = f'https://api.telegram.org/bot{TOKEN}'

print("=== getWebhookInfo ===")
webhook_info = requests.post(f'{base}/getWebhookInfo').json()
print(json.dumps(webhook_info, indent=2))

if webhook_info.get('result', {}).get('url'):
    print("\n⚠️ Webhook is ACTIVE! Deleting it...")
    del_resp = requests.post(f'{base}/deleteWebhook').json()
    print("deleteWebhook response:", del_resp)

print("\n=== Clearing pending updates ===")
updates = requests.post(f'{base}/getUpdates?limit=100').json()
if updates.get('result'):
    update_ids = [u['update_id'] for u in updates['result']]
    print(f"Found {len(update_ids)} pending updates, clearing...")
    last_id = max(update_ids) if update_ids else None
    if last_id:
        clear = requests.post(f'{base}/getUpdates?offset={last_id+1}').json()
        print(f"Cleared up to update_id {last_id}")
else:
    print("No pending updates found")

print("\n✅ Bot is ready for polling!")
