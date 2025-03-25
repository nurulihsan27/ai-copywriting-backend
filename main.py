from fastapi import FastAPI, HTTPException
import openai
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")

# Setup MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["ai_copywriting"]
users_collection = db["users"]

app = FastAPI()

# ✅ Tambahkan endpoint root untuk menghindari error 404
@app.get("/")
def read_root():
    return {"message": "Welcome to AI Copywriting API"}

@app.post("/generate/")
async def generate_copywriting(user_id: str, nama_produk: str, deskripsi: str, manfaat: str, gaya_bahasa: str, platform: str, jenis_konten: str, keterangan: str = ""):
    user = users_collection.find_one({"user_id": user_id})

    if not user or user["generate_quota"] <= 0:
        raise HTTPException(status_code=400, detail="Kuota generate habis, silakan beli paket.")

    prompt = f"""
    Buatkan copywriting untuk produk "{nama_produk}".
    Deskripsi: {deskripsi}.
    Manfaat: {manfaat}.
    Gaya bahasa: {gaya_bahasa}.
    Platform: {platform}.
    Jenis konten: {jenis_konten}.
    {f"Keterangan tambahan: {keterangan}" if keterangan else ""}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    generated_text = response["choices"][0]["message"]["content"]

    users_collection.update_one({"user_id": user_id}, {"$inc": {"generate_quota": -1}})

    return {"copywriting": generated_text}
