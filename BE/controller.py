import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import os
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Configuramos el cliente apuntando a Hugging Face
# Asegurate de reemplazar "TU_TOKEN_AQUI" por el tuyo (el que generaste antes).
# En producción, esto se lee de variables de entorno (.env)
TOKEN_HF = os.environ.get("HF_TOKEN", "TU_TOKEN_AQUI") 

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="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",
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analisis-bonos")
async def analizar_bonos(archivo: UploadFile = File(...)):
    contenido = await archivo.read()
    df = pd.read_csv(io.BytesIO(contenido))
    
    df = df.dropna()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    metricas = df.groupby('Ticker').agg(
        precio_promedio=('Cierre', 'mean'),
        volatilidad=('Cierre', 'std')
    ).reset_index()
    
    contexto_datos = metricas.to_string(index=False)
    
    prompt = f"""
    Actúa como un analista financiero. Basado en las siguientes métricas de bonos y obligaciones negociables:
    
    {contexto_datos}
    
    Escribe un resumen ejecutivo breve destacando qué activo tiene mayor volatilidad y si representa una oportunidad de mercado.
    IMPORTANTE: Tu respuesta debe estar formateada estrictamente en HTML (usa <h3>, <p>, <ul>, <b>). No uses markdown ni incluyas la etiqueta ```html al principio.
    """
    
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct", 
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=150
    )
    
    # 3. Extracción de la respuesta
    texto_generado = completion.choices[0].message.content.strip()
    
    return {
        "metricas": metricas.to_dict(orient="records"),
        "analisis_llm": texto_generado
    }

if __name__ == "__main__":
    uvicorn.run("controller:app", host="127.0.0.1", port=8000, reload=True)