import hashlib
import json
import uuid
from time import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from FileStore import FileStorage

class Blockchain:
    def __init__(self):
        self.storage = FileStorage("blockchain_data.json")
        chain = self.storage.read()
        if not chain:
            self.create_block(previous_hash='1', proof=100, record_data={
                "evento": "Gênesis - Sistema de Castanha Iniciado",
                "status_validacao": "Sistema Online"
            })

    def create_block(self, proof: int, previous_hash: str, record_data: dict):
        chain = self.storage.read()
        block = {
            'index': len(chain) + 1,
            'timestamp': time(),
            'dados': record_data,
            'proof': proof,
            'previous_hash': previous_hash
        }
        
        hash_bloco = self.hash(block)
        block['hash_bloco'] = hash_bloco
        block['id'] = hash_bloco 
        
        self.storage.create(block)
        return block

    def get_previous_block(self):
        chain = self.storage.read()
        return chain[-1]

    def hash(self, block):
        block_copy = block.copy()
        block_copy.pop('hash_bloco', None)
        block_copy.pop('id', None)
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000':
                return new_proof
            new_proof += 1

app = FastAPI(title="Blockchain Castanha da Amazônia")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

blockchain = Blockchain()

class EventoCastanha(BaseModel):
    id_produto: str
    origem_coleta: Optional[str] = ""
    comunidade_fornecedora: Optional[str] = ""
    peso_lote: float = 0.0
    tamanho: str = "Média"
    umidade: float = 0.0
    status_produto: str = "Em processamento"
    id_etapa: str
    evento: str
    usuario_responsavel: str
    dispositivo_origem: str
    localizacao: str
    nivel_confiabilidade: float = 100.0

@app.post("/mine_event/")
def mine_event(req: EventoCastanha):
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    
    dados = req.dict()
    dados["id_registro"] = str(uuid.uuid4())
    dados["timestamp_evento"] = time()
    
    block = blockchain.create_block(proof, prev_hash, dados)
    return {"codigo_blockchain": block['hash_bloco'], "bloco": block}

@app.get("/buscar/{termo}")
def buscar_geral(termo: str):
    termo = termo.strip()
    chain = blockchain.storage.read()
    
    for b in chain:
        if (b.get('id') == termo or 
            b.get('hash_bloco') == termo or 
            b.get('dados', {}).get('id_produto') == termo):
            
            id_alvo = b.get('dados', {}).get('id_produto')
            historico = [bl for bl in chain if bl.get('dados', {}).get('id_produto') == id_alvo]
            tipo = "Hash" if (b.get('id') == termo or b.get('hash_bloco') == termo) else "Lote"
            
            return {"id_produto": id_alvo, "historico": historico, "tipo_busca": tipo}
            
    raise HTTPException(status_code=404, detail="Registro não encontrado na Blockchain.")

@app.get("/chain/")
def full_chain():
    return blockchain.storage.read()