import requests
import os
from datetime import datetime, timezone
import time
import base64

EBAY_CLIENT_ID     = os.environ["EBAY_CLIENT_ID"]
EBAY_CLIENT_SECRET = os.environ["EBAY_CLIENT_SECRET"]
SUPABASE_URL       = os.environ["SUPABASE_URL"]
SUPABASE_KEY       = os.environ["SUPABASE_SERVICE_KEY"]

LISTINGS_PER_CARD  = 5

CARDS = [
    "NRSA01-SE-001", "NRSA01-SE-002", "NRSA01-SE-003", "NRSA01-SE-004",
    "NRSA02-SE-001", "NRSA02-SE-002", "NRSA02-SE-003", "NRSA02-SE-004",
    "NRSA03-SE-001", "NRSA03-SE-002", "NRSA03-SE-003", "NRSA03-SE-004",
    "NRV01-SE-001", "NRV01-SE-002", "NRV01-SE-003", "NRV01-SE-004",
    "NREA01-CR-001", "NREA01-CR-002", "NREA01-CR-003", "NREA01-CR-004",
    "NREA02-CR-001", "NREA02-CR-002", "NREA02-CR-003", "NREA02-CR-004",
    "NRSA01-BP-001", "NRSA01-BP-002", "NRSA01-BP-003", "NRSA01-BP-004",
    "NRSA01-BP-005", "NRSA01-BP-006", "NRSA01-BP-007",
    "NRSA02-BP-001", "NRSA02-BP-002", "NRSA02-BP-003", "NRSA02-BP-004",
    "NRSA02-BP-005", "NRSA02-BP-006", "NRSA02-BP-007",
    "NRSA03-BP-001", "NRSA03-BP-002", "NRSA03-BP-003", "NRSA03-BP-004",
    "NRSA03-BP-005", "NRSA03-BP-006", "NRSA03-BP-007",
    "NRV01-BP-001", "NRV01-BP-002", "NRV01-BP-003", "NRV01-BP-004",
    "NRV01-BP-005", "NRV01-BP-006", "NRV01-BP-007",
    "NREA01-MR-001", "NREA01-MR-002", "NREA01-MR-003", "NREA01-MR-004",
    "NREA02-MR-001", "NREA02-MR-002", "NREA02-MR-003", "NREA02-MR-004",
    "NRSA01-MR-001", "NRSA01-MR-002", "NRSA01-MR-003", "NRSA01-MR-004",
    "NRSA01-MR-005", "NRSA01-MR-006",
    "NRSA02-MR-001", "NRSA02-MR-002", "NRSA02-MR-003", "NRSA02-MR-004",
    "NRSA02-MR-005", "NRSA02-MR-006", "NRSA02-MR-007",
    "NRSA03-MR-001", "NRSA03-MR-002", "NRSA03-MR-003", "NRSA03-MR-004",
    "NRSA03-MR-005", "NRSA03-MR-006", "NRSA03-MR-007", "NRSA03-MR-008",
    "NRV01-MR-001", "NRV01-MR-002", "NRV01-MR-003", "NRV01-MR-004",
    "NRV01-MR-005", "NRV01-MR-006",
    "NREA01-SP-001", "NREA01-SP-002", "NREA01-SP-003", "NREA01-SP-004",
    "NRSA01-SP-001", "NRSA01-SP-002", "NRSA01-SP-003", "NRSA01-SP-004",
    "NRSA02-SP-001", "NRSA02-SP-002", "NRSA02-SP-003", "NRSA02-SP-004",
    "NRV01-SP-001", "NRV01-SP-002", "NRV01-SP-003", "NRV01-SP-004",
    "NREA01-AR-001", "NREA01-AR-002", "NREA01-AR-003", "NREA01-AR-004",
    "NREA01-AR-005", "NREA01-AR-006", "NREA01-AR-007", "NREA01-AR-008",
    "NREA01-AR-009", "NREA01-AR-010",
    "NREA02-AR-001", "NREA02-AR-002", "NREA02-AR-003", "NREA02-AR-004",
    "NREA02-AR-005", "NREA02-AR-006", "NREA02-AR-007", "NREA02-AR-008",
    "NREA02-AR-009", "NREA02-AR-010",
    "NRSA02-AR-001", "NRSA02-AR-002", "NRSA02-AR-003", "NRSA02-AR-004",
    "NRSA02-AR-005", "NRSA02-AR-006", "NRSA02-AR-007", "NRSA02-AR-008",
    "NRSA02-AR-009", "NRSA02-AR-010",
    "NRSA03-AR-001", "NRSA03-AR-002", "NRSA03-AR-003", "NRSA03-AR-004",
    "NRSA03-AR-005", "NRSA03-AR-006", "NRSA03-AR-007",
    "NRSA03-ASP-001", "NRSA03-ASP-002", "NRSA03-ASP-003", "NRSA03-ASP-004",
    "NRSA03-ASP-005", "NRSA03-ASP-006", "NRSA03-ASP-007", "NRSA03-ASP-008",
    "NREA02-◇UR-001", "NREA02-◇UR-002", "NREA02-◇UR-003", "NREA02-◇UR-004",
    "NRSA03-◇UR-001", "NRSA03-◇UR-002", "NRSA03-◇UR-003", "NRSA03-◇UR-004",
    "NRSA03-◇UR-005", "NRSA03-◇UR-006", "NRSA03-◇UR-007", "NRSA03-◇UR-008",
    "NRSA03-◇UR-009", "NRSA03-◇UR-010", "NRSA03-◇UR-011",
    "NREA-PR-001", "NREA-PR-002", "NREA-PR-003",
    "NRIE-PR-002",
    "NRSA-PR-001", "NRSA-PR-003", "NRSA-PR-004", "NRSA-PR-005",
    "NRSA-PR-006", "NRSA-PR-009", "NRSA-PR-010",
    "NRSA-◇PR-002",
]

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

def delete_listings_for_card(card_id):
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/card_market_listings",
        headers=sb_headers(),
        params={"card_identifier": f"eq.{card_id}"},
    )
    if r.status_code not in (200, 204):
        print(f"  ⚠️  Delete failed for {card_id}: {r.status_code} {r.text}")

def insert_listings(rows):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/card_market_listings",
        headers={**sb_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
        json=rows,
    )
    if r.status_code not in (200, 201, 204):
        print(f"  ⚠️  Insert failed: {r.status_code} {r.text}")

def get_access_token():
    credentials = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope",
    )
    if r.status_code == 200:
        print("✅ eBay token received")
        return r.json().get("access_token")
    print(f"❌ Token error: {r.status_code} — {r.text}")
    return None

def make_affiliate_url(original_url):
    return (
        f"https://rover.ebay.com/rover/1/711-53200-19255-0/1"
        f"?mpre={requests.utils.quote(original_url)}"
        f"&campid=5339154394&toolid=10001&mkrid=711-53200-19255-0&mkcid=1"
    )

def search_listings(token, card_id):
    keyword = card_id.replace("◇", "diamond ")
    r = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        },
        params={
            "q": keyword,
            "limit": LISTINGS_PER_CARD,
            "sort": "price",
            "filter": "buyingOptions:{FIXED_PRICE}",
        },
    )
    if r.status_code == 200:
        return r.json().get("itemSummaries", [])
    print(f"  ⚠️  eBay error {r.status_code} for {card_id}")
    return []

def run():
    print("=" * 50)
    print(f"🚀 eBay Listings Sync — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Cards: {len(CARDS)} | Listings per card: {LISTINGS_PER_CARD}")
    print("=" * 50)

    token = get_access_token()
    if not token:
        raise SystemExit("❌ No eBay token, aborting.")

    now = datetime.now(timezone.utc).isoformat()
    total_inserted = 0

    for i, card_id in enumerate(CARDS, 1):
        print(f"\n[{i}/{len(CARDS)}] {card_id}")
        items = search_listings(token, card_id)

        if not items:
            print("  — No listings found, skipping.")
            time.sleep(1)
            continue

        rows = []
        for item in items:
            price = item.get("price", {}).get("value")
            if not price:
                continue
            original_url = item.get("itemWebUrl", "")
            rows.append({
                "card_identifier": card_id,
                "ebay_item_id":    item.get("itemId", ""),
                "title":           item.get("title", ""),
                "price":           float(price),
                "currency":        item.get("price", {}).get("currency", "USD"),
                "url":             make_affiliate_url(original_url) if original_url else "",
                "updated_at":      now,
            })

        if rows:
            delete_listings_for_card(card_id)
            insert_listings(rows)
            total_inserted += len(rows)
            for row in rows:
                print(f"  ✅ {row['title'][:55]} — {row['price']} {row['currency']}")

        time.sleep(1)

    print(f"\n✅ Done! {total_inserted} listings synced to DB.")

if __name__ == "__main__":
    run()
