# main.py - FlashInvoice v0.8.1 (Final - Exit-Ready + Secure)
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import httpx
import time
import os
import hashlib
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FlashInvoice.xyz", version="0.8.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://flashinvoice.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIG ====================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LNBITS_API_KEY = os.getenv("LNBITS_API_KEY")
LNBITS_URL = os.getenv("LNBITS_URL", "https://legend.lnbits.com/api/v1/payments").rstrip("/")
NOSTR_PRIVATE_KEY = os.getenv("NOSTR_PRIVATE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rate Limiting amélioré (avec nettoyage)
rate_limit_store = {}

def check_rate_limit(key: str, limit: int = 30):
    now = time.time()
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    
    # Nettoyage automatique des anciennes entrées
    rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < 60]
    
    if len(rate_limit_store[key]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit_store[key].append(now)

# ==================== LIGHTNING PROVIDER (Abstraction) ====================
class LightningProvider:
    async def create_invoice(self, amount_sats: int, memo: str):
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.post(
                    f"{LNBITS_URL}",
                    json={"out": False, "amount": amount_sats, "memo": memo},
                    headers={"X-Api-Key": LNBITS_API_KEY}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail="Lightning provider error")

lightning = LightningProvider()

# ==================== ENDPOINTS ====================
@app.post("/create-invoice")
async def create_invoice(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    agent_pubkey = body.get("agent_pubkey")
    task_hash = body.get("task_hash")
    amount_usd = body.get("amount_usd", 0.10)
    description = body.get("description", "M2M Payment")

    if not agent_pubkey or not task_hash:
        raise HTTPException(400, "Missing agent_pubkey or task_hash")

    check_rate_limit(agent_pubkey, limit=5)

    # === IDEMPOTENCE ===
    existing = supabase.table("invoices").select("*") \
        .eq("agent_sender_pubkey", agent_pubkey) \
        .eq("task_hash", task_hash) \
        .eq("status", "pending") \
        .gt("created_at", (datetime.utcnow() - timedelta(minutes=10)).isoformat()) \
        .execute()

    if existing.data:
        inv = existing.data[0]
        return JSONResponse(
            status_code=402,
            content={"invoice": inv["bolt11"]},
            headers={"WWW-Authenticate": f'L402 invoice="{inv["bolt11"]}"'}
        )

    # === CRÉATION FACTURE ===
    sats_per_usd = 2500.0  # TODO: Remplacer par get_sats_rate()
    amount_sats = max(10, int(amount_usd * sats_per_usd))

    ln_data = await lightning.create_invoice(amount_sats, description)
    bolt11 = ln_data["payment_request"]
    payment_hash = ln_data["payment_hash"]

    invoice_id = hashlib.sha256(f"{agent_pubkey}{payment_hash}".encode()).hexdigest()

    supabase.table("invoices").insert({
        "id": invoice_id,
        "agent_sender_pubkey": agent_pubkey,
        "task_hash": task_hash,
        "amount_sats": amount_sats,
        "bolt11": bolt11,
        "payment_hash": payment_hash,
        "status": "pending",
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return JSONResponse(
        status_code=402,
        content={"invoice": bolt11},
        headers={"WWW-Authenticate": f'L402 invoice="{bolt11}"'}
    )

@app.post("/webhook/lnbits")
async def lnbits_webhook(payload: dict):
    payment_hash = payload.get("payment_hash")
    preimage = payload.get("preimage")

    if not payment_hash or not preimage:
        raise HTTPException(400, "Missing payment data")

    if hashlib.sha256(bytes.fromhex(preimage)).hexdigest() != payment_hash:
        raise HTTPException(400, "Invalid preimage")

    result = supabase.table("invoices").update({
        "status": "paid",
        "preimage": preimage,
        "paid_at": datetime.utcnow().isoformat()
    }).eq("payment_hash", payment_hash).execute()

    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.8.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
