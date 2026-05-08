import hashlib
import json
import uuid
from time import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List


# ESTRUTURA DA BLOCKCHAIN

class Blockchain:
    def __init__(self):
        self.chain = []
        # Bloco Gênesis
        self.create_block(previous_hash='1', proof=100, record_data={
            "evento": "Gênesis - Início da Cadeia",
            "status_validacao": "Sistema Inicializado"
        })

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


# MODELAGEM DE DADOS (BASEADA NO CSV)

class EventoCastanha(BaseModel):
    # : PRODUTO
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

    # ETAPAS
    id_etapa: str  # coleta_castanha_in_natura, inspecao_entrada, etc.

    # REGISTRO
    evento: str
    usuario_responsavel: str
    dispositivo_origem: str
    localizacao: str
    nivel_confiabilidade: float = 100.0

app = FastAPI(title="Blockchain Castanha da Amazônia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain()

@app.get("/")
def root():
    return {"status": "Online", "documentacao": "/docs"}

@app.post("/mine_event/")
def mine_event(req: EventoCastanha):
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block['proof'])
    prev_hash = blockchain.hash(prev_block)
    
    # Gerar campos automáticos do Registro
    dados = req.dict()
    dados["id_registro"] = str(uuid.uuid4())
    dados["timestamp_evento"] = time()
    dados["status_validacao"] = "Validado"
    dados["assinatura_digital"] = hashlib.sha256(str(dados).encode()).hexdigest()
    
    block = blockchain.create_block(proof, prev_hash, dados)
    
    return {
        "codigo_blockchain": block['hash_bloco'],
        "qr_code": f"https://rastreio.am/lote/{req.id_produto}",
        "bloco": block
    }

@app.get("/produto/{id_produto}")
def get_history(id_produto: str):
    history = [b for b in blockchain.chain if b.get('dados', {}).get('id_produto') == id_produto]
    return {"id_produto": id_produto, "historico": history}

@app.get("/chain/")
def full_chain():
    return blockchain.chain