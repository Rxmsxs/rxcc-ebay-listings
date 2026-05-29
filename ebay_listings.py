import requests
import os
import re
from datetime import datetime, timezone
import time
import base64

# Maps set prefix → human-readable series used in eBay titles
SET_TO_SERIES = {
    "NRSA01": "Series 1",
    "NRSA02": "Series 2",
    "NRSA03": "Series 3",
    "NREA01": "Earth 1",
    "NREA02": "Earth 2",
    "NRV01":  "NRV01",
}

# Regex to find any card identifier in a listing title
# Matches patterns like: NRSA03-ASP-007, NRZ06-BP-031, NRB09-CR-001, etc.
_IDENT_RE = re.compile(r'\b(NR[A-Z0-9]+)[-–]([\w◇]+)[-–](\d+)', re.IGNORECASE)

EBAY_CLIENT_ID     = os.environ["EBAY_CLIENT_ID"]
EBAY_CLIENT_SECRET = os.environ["EBAY_CLIENT_SECRET"]
SUPABASE_URL       = os.environ["SUPABASE_URL"]
SUPABASE_KEY       = os.environ["SUPABASE_SERVICE_KEY"]

LISTINGS_PER_CARD = 5

CARDS = [
    # SE
    "NRSA01-SE-001", "NRSA01-SE-002", "NRSA01-SE-003", "NRSA01-SE-004",
    "NRSA02-SE-001", "NRSA02-SE-002", "NRSA02-SE-003", "NRSA02-SE-004",
    "NRSA03-SE-001", "NRSA03-SE-002", "NRSA03-SE-003", "NRSA03-SE-004",
    "NRV01-SE-001", "NRV01-SE-002", "NRV01-SE-003", "NRV01-SE-004",
    # CR
    "NREA01-CR-001", "NREA01-CR-002", "NREA01-CR-003", "NREA01-CR-004",
    "NREA02-CR-001", "NREA02-CR-002", "NREA02-CR-003", "NREA02-CR-004",
    # BP
    "NRSA01-BP-001", "NRSA01-BP-002", "NRSA01-BP-003", "NRSA01-BP-004",
    "NRSA01-BP-005", "NRSA01-BP-006", "NRSA01-BP-007",
    "NRSA02-BP-001", "NRSA02-BP-002", "NRSA02-BP-003", "NRSA02-BP-004",
    "NRSA02-BP-005", "NRSA02-BP-006", "NRSA02-BP-007",
    "NRSA03-BP-001", "NRSA03-BP-002", "NRSA03-BP-003", "NRSA03-BP-004",
    "NRSA03-BP-005", "NRSA03-BP-006", "NRSA03-BP-007",
    "NRV01-BP-001", "NRV01-BP-002", "NRV01-BP-003", "NRV01-BP-004",
    "NRV01-BP-005", "NRV01-BP-006", "NRV01-BP-007",
    # MR
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
    # SP
    "NREA01-SP-001", "NREA01-SP-002", "NREA01-SP-003", "NREA01-SP-004",
    "NRSA01-SP-001", "NRSA01-SP-002", "NRSA01-SP-003", "NRSA01-SP-004",
    "NRSA02-SP-001", "NRSA02-SP-002", "NRSA02-SP-003", "NRSA02-SP-004",
    "NRV01-SP-001", "NRV01-SP-002", "NRV01-SP-003", "NRV01-SP-004",
    # AR
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
    # ASP
    "NRSA03-ASP-001", "NRSA03-ASP-002", "NRSA03-ASP-003", "NRSA03-ASP-004",
    "NRSA03-ASP-005", "NRSA03-ASP-006", "NRSA03-ASP-007", "NRSA03-ASP-008",
    # diamond ASP
    "NRSA03-◇ASP-001", "NRSA03-◇ASP-002", "NRSA03-◇ASP-003", "NRSA03-◇ASP-004",
    "NRSA03-◇ASP-005", "NRSA03-◇ASP-006", "NRSA03-◇ASP-007", "NRSA03-◇ASP-008",
    # diamond UR
    "NREA02-◇UR-001", "NREA02-◇UR-002", "NREA02-◇UR-003", "NREA02-◇UR-004",
    "NRSA03-◇UR-001", "NRSA03-◇UR-002", "NRSA03-◇UR-003", "NRSA03-◇UR-004",
    "NRSA03-◇UR-005", "NRSA03-◇UR-006", "NRSA03-◇UR-007", "NRSA03-◇UR-008",
    "NRSA03-◇UR-009", "NRSA03-◇UR-010", "NRSA03-◇UR-011",
    # PR
    "NREA-PR-001", "NREA-PR-002", "NREA-PR-003",
    "NRIE-PR-002",
    "NRSA-PR-001", "NRSA-PR-003", "NRSA-PR-004", "NRSA-PR-005",
    "NRSA-PR-006", "NRSA-PR-009", "NRSA-PR-010",
    "NRSA-◇PR-002",
]

# ---------------------------------------------------------------------------
# Supabase: fetch display_name for every card identifier
# ---------------------------------------------------------------------------

def fetch_card_names():
    """Returns dict: { "NRSA03-ASP-007": "Gaara", ... }"""
    url = f"{SUPABASE_URL}/rest/v1/cards"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    result = {}
    offset = 0
    limit  = 1000
    while True:
        r = requests.get(
            url, headers=headers,
            params={
                "select": "name,display_name",
                "language": "eq.english",
                "limit": limit,
                "offset": offset,
            },
        )
        if r.status_code != 200:
            print(f"⚠️  Could not fetch card names: {r.status_code}")
            break
        batch = r.json()
        for card in batch:
            ident   = card.get("name", "")
            display = card.get("display_name", "").strip()   # trim spaces
            if ident and display:
                result[ident] = display
        if len(batch) < limit:
            break
        offset += limit
    print(f"✅ Loaded {len(result)} card names from Supabase")
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_set_prefix(card_id):
    """Extract set prefix, e.g. NRSA03-ASP-007 → NRSA03"""
    clean = card_id.replace("◇", "")
    return clean.split("-")[0] if "-" in clean else ""


def get_rarity(card_id):
    """Extract rarity, e.g. NRSA03-ASP-007 → ASP"""
    clean = card_id.replace("◇", "")
    parts = clean.split("-")
    return parts[1] if len(parts) >= 2 else ""


def get_card_number(card_id):
    """Extract card number, e.g. NRSA03-ASP-007 → 007"""
    clean = card_id.replace("◇", "")
    parts = clean.split("-")
    return parts[2] if len(parts) >= 3 else ""


def get_search_keyword(card_id, card_names):
    display_name = card_names.get(card_id, "").strip()
    rarity       = get_rarity(card_id)
    set_prefix   = get_set_prefix(card_id)
    series_label = SET_TO_SERIES.get(set_prefix, set_prefix)
    is_diamond   = "◇" in card_id

    if display_name:
        if is_diamond:
            return f"{display_name} diamond {rarity} {series_label} naruto kayou"
        return f"{display_name} {rarity} {series_label} naruto kayou"

    # Fallback: identifier-based search
    if is_diamond:
        return card_id.replace("◇", "") + " diamond"
    return card_id


def is_valid_result(item, card_id, card_names):
    title      = item.get("title", "").lower()
    is_diamond = "◇" in card_id

    clean_id    = card_id.replace("◇", "")
    set_prefix  = get_set_prefix(card_id)
    rarity      = get_rarity(card_id)
    card_number = get_card_number(card_id)

    # --- HARD EXCLUSION: title contains a different card identifier ---
    # If ANY identifier pattern is found in the title, it must match ours.
    # e.g. listing says "NRSA03-ASP-034" but we want "NRSA03-ASP-002" → reject
    # e.g. listing says "NRZ06-SE-015" but we want "NRSA01-SE-003" → reject
    for match in _IDENT_RE.finditer(title):
        found_set    = match.group(1).upper()
        found_rarity = match.group(2).upper().replace("◇", "")
        found_num    = match.group(3).lstrip("0") or "0"
        our_num      = card_number.lstrip("0") or "0"
        our_rarity   = rarity.upper()
        our_set      = set_prefix.upper()

        # If set AND rarity AND number all match → fine
        if (found_set == our_set and
                found_rarity == our_rarity and
                found_num == our_num):
            continue
        # If set AND rarity match but number differs → definitely wrong card
        if found_set == our_set and found_rarity == our_rarity:
            return False
        # If set doesn't match at all → different series → reject
        if found_set != our_set:
            return False

    # --- 1. Identifier check (strongest positive signal) ---
    if clean_id.lower() in title:
        return True
    relaxed_id = clean_id.lower().replace("-", " ", 1)
    if relaxed_id in title:
        return True

    # --- 2. display_name + rarity + series check ---
    display_name = card_names.get(card_id, "").strip()
    series_label = SET_TO_SERIES.get(set_prefix, "").lower()

    if display_name and rarity:
        name_words    = display_name.lower().split()
        name_match    = all(w in title for w in name_words)
        rarity_match  = rarity.lower() in title
        naruto_match  = "naruto" in title or "kayou" in title
        # For PR cards series check is relaxed (PRs rarely include full set name)
        series_match  = (series_label in title) or (rarity.lower() == "pr")

        if name_match and rarity_match and naruto_match and series_match:
            if is_diamond:
                return "diamond" in title or "💎" in title
            return True

    return False


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

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
        print(f"  ⚠️ Delete failed for {card_id}: {r.status_code} {r.text}")


def insert_listings(rows):
    # on_conflict=ebay_item_id + ignore-duplicates: silently skips duplicate item IDs
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/card_market_listings?on_conflict=ebay_item_id",
        headers={**sb_headers(), "Prefer": "resolution=ignore-duplicates,return=minimal"},
        json=rows,
    )
    if r.status_code not in (200, 201, 204):
        print(f"  ⚠️ Insert failed: {r.status_code} {r.text}")


# ---------------------------------------------------------------------------
# eBay helpers
# ---------------------------------------------------------------------------

def get_access_token():
    credentials = base64.b64encode(
        f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()
    ).decode()
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
    separator = "&" if "?" in original_url else "?"
    return (
        f"{original_url}{separator}"
        "mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5339154394&toolid=10001"
    )


def get_identifier_keyword(card_id):
    """Pure identifier-based search — catches listings that only include the card ID."""
    if "◇" in card_id:
        return card_id.replace("◇", "") + " diamond"
    return card_id


def _ebay_search(token, query, limit):
    """Single eBay API call; returns list of itemSummaries."""
    r = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        },
        params={
            "q": query,
            "limit": limit,
            "sort": "price",
            "filter": "buyingOptions:{FIXED_PRICE}",
        },
    )
    if r.status_code == 200:
        return r.json().get("itemSummaries", [])
    print(f"  ⚠️ eBay error {r.status_code} for query: {query[:60]}")
    return []


def search_listings(token, card_id, card_names):
    """
    Dual search:
      1. Identifier query  → finds listings that contain only the card ID (e.g. NRSA01-SP-001)
      2. Display-name query → finds listings that use character name + series
    Results are merged, deduplicated by itemId, sorted by price.
    """
    seen_ids = set()
    all_items = []

    id_query   = get_identifier_keyword(card_id)
    name_query = get_search_keyword(card_id, card_names)

    # --- Search 1: identifier ---
    print(f"  🔍 ID query:   {id_query}")
    for item in _ebay_search(token, id_query, LISTINGS_PER_CARD):
        iid = item.get("itemId", "")
        if iid and iid not in seen_ids:
            seen_ids.add(iid)
            all_items.append(item)

    time.sleep(0.5)  # small pause between the two calls

    # --- Search 2: display-name (skip if identical to id_query) ---
    if name_query != id_query:
        print(f"  🔍 Name query: {name_query}")
        for item in _ebay_search(token, name_query, LISTINGS_PER_CARD):
            iid = item.get("itemId", "")
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                all_items.append(item)

    # Sort merged pool by price (cheapest first)
    def _price(item):
        try:
            return float(item.get("price", {}).get("value", 9999999))
        except (TypeError, ValueError):
            return 9999999

    all_items.sort(key=_price)
    return all_items


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    print("=" * 50)
    print(f"🚀 eBay Listings Sync — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Cards: {len(CARDS)} | Listings per card: {LISTINGS_PER_CARD}")
    print("=" * 50)

    card_names = fetch_card_names()

    token = get_access_token()
    if not token:
        raise SystemExit("❌ No eBay token, aborting.")

    now = datetime.now(timezone.utc).isoformat()
    total_inserted = 0
    total_skipped  = 0

    for i, card_id in enumerate(CARDS, 1):
        display = card_names.get(card_id, "")
        label   = f"{card_id}" + (f" ({display})" if display else "")
        print(f"\n[{i}/{len(CARDS)}] {label}")

        # search_listings does dual search (identifier + display-name) and prints queries
        items = search_listings(token, card_id, card_names)

        if not items:
            print("  — No listings found, skipping.")
            time.sleep(1)
            continue

        rows = []
        seen_item_ids = set()
        for item in items:
            price   = item.get("price", {}).get("value")
            item_id = item.get("itemId", "")
            if not price or not item_id:
                continue
            if item_id in seen_item_ids:
                continue

            if not is_valid_result(item, card_id, card_names):
                print(f"  ⚠️ Invalid: '{item.get('title', '')[:60]}'")
                total_skipped += 1
                continue

            seen_item_ids.add(item_id)
            original_url = item.get("itemWebUrl", "")
            rows.append({
                "card_identifier": card_id,
                "ebay_item_id":    item_id,
                "title":           item.get("title", ""),
                "price":           float(price),
                "currency":        item.get("price", {}).get("currency", "USD"),
                "url":             make_affiliate_url(original_url) if original_url else "",
                "updated_at":      now,
            })

            # cap at LISTINGS_PER_CARD valid rows (already sorted cheapest-first)
            if len(rows) >= LISTINGS_PER_CARD:
                break

        if rows:
            delete_listings_for_card(card_id)
            insert_listings(rows)
            total_inserted += len(rows)
            for row in rows:
                print(f"  ✅ {row['title'][:55]} — {row['price']} {row['currency']}")
        else:
            print("  — All results invalid, skipping.")

        time.sleep(0.5)  # reduced: we already sleep 0.5 between dual searches

    print(f"\n✅ Done! {total_inserted} listings inserted | {total_skipped} invalid skipped.")


if __name__ == "__main__":
    run()
