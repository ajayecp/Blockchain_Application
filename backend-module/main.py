import hashlib
import json
import uuid
import os
from time import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

# Nome do arquivo onde os dados serão armazenados
DB_FILE = "blockchain_data.json"

# ==========================================
# Lógica da Blockchain com Persistência
# ==========================================
class Blockchain:
    def __init__(self):
        self.chain = []
        if os.path.exists(DB_FILE):
            self.load_from_disk()
        else:
            # Se o arquivo não existir, cria o Bloco Gênesis
            self.create_block(previous_hash='1', proof=100, record_data={
                "evento": "Gênesis - Sistema de Castanha Iniciado",
                "status_validacao": "Sistema Online"
            })

    def save_to_disk(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.chain, f, indent=4, ensure_ascii=False)

    def load_from_disk(self):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                self.chain = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            self.chain = []

    def create_block(self, proof: int, previous_hash: str, record_data: dict):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'dados': record_data,
            'proof': proof,
            'previous_hash': previous_hash
        }
        block['hash_bloco'] = self.hash(block)
        self.chain.append(block)
        self.save_to_disk() # Salva no arquivo a cada novo bloco
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash(self, block):
        block_copy = block.copy()
        if 'hash_bloco' in block_copy: del block_copy['hash_bloco']
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000': return new_proof
            new_proof += 1

# ==========================================
# Modelagem e API
# ==========================================
class EventoCastanha(BaseModel):
    id_produto: str
    origem_coleta: Optional[str] = ""
    comunidade_fornecedora: Optional[str] = ""
    data_coleta: Optional[str] = ""
    peso_lote: float = 0.0
    quantidade_castanhas: int = 0
    tamanho: str = "Média"
    classificacao_qualidade: str = "N/A"
    umidade: float = 0.0
    temperatura_armazenamento: float = 0.0
    status_produto: str = "Em processamento"
    certificacao_sustentavel: Optional[str] = ""
    pegada_carbono: Optional[str] = ""
    id_etapa: str
    evento: str
    usuario_responsavel: str
    dispositivo_origem: str
    localizacao: str
    nivel_confiabilidade: float = 100.0

app = FastAPI(title="Blockchain Castanha V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

blockchain = Blockchain()

@app.post("/mine_event/")
def mine_event(req: EventoCastanha):
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    
    dados = req.dict()
    dados["id_registro"] = str(uuid.uuid4())
    dados["timestamp_evento"] = time()
    dados["status_validacao"] = "Validado"
    dados["assinatura_digital"] = hashlib.sha256(str(dados).encode()).hexdigest()
    
    block = blockchain.create_block(proof, prev_hash, dados)
    return {"codigo_blockchain": block['hash_bloco'], "bloco": block}

@app.get("/produto/{id_produto}")
def get_history(id_produto: str):
    # Busca no arquivo/memória todos os blocos do lote
    history = [b for b in blockchain.chain if b.get('dados', {}).get('id_produto') == id_produto]
    if not history:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return {"id_produto": id_produto, "historico": history}

@app.get("/export_json/")
def export_json():
    # Rota extra para baixar o arquivo bruto
    return blockchain.chain