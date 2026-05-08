import hashlib
import json
import uuid
from time import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# ==========================================
# Lógica da Blockchain
# ==========================================
class Blockchain:
    def __init__(self):
        self.chain = []
        # Bloco Gênesis
        self.create_block(previous_hash='1', proof=100, record_data={
            "id_registro": "GENESIS", "id_produto": "N/A", "id_etapa": "inicio",
            "evento": "Criação da Blockchain", "usuario_responsavel": "Sistema",
            "timestamp_evento": time(), "status_validacao": "Validado", "nivel_confiabilidade": 100.0
        })

    def create_block(self, proof: int, previous_hash: str, record_data: dict):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'dados_registro': record_data,
            'proof': proof,
            'previous_hash': previous_hash
        }
        
        # Gerar a assinatura digital / hash do bloco atual
        block['hash_bloco'] = self.hash(block)
        
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def hash(self, block):
        # Exclui o próprio hash da conta caso exista no dicionário
        block_copy = block.copy()
        if 'hash_bloco' in block_copy:
            del block_copy['hash_bloco']
        encoded_block = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

# ==========================================
# Modelagem de Dados (Pydantic) baseada no seu CSV
# ==========================================
class EventoCastanha(BaseModel):
    # Produto
    id_produto: str
    origem_coleta: Optional[str] = ""
    comunidade_fornecedora: Optional[str] = ""
    peso_lote: Optional[float] = 0.0
    quantidade_castanhas: Optional[int] = 0
    tamanho: Optional[str] = ""  # Pequena, média ou grande
    classificacao_qualidade: Optional[str] = ""
    umidade: Optional[float] = 0.0
    temperatura_armazenamento: Optional[float] = 0.0
    status_produto: str = "Em processamento"
    certificacao_sustentavel: Optional[str] = ""
    pegada_carbono: Optional[str] = "0kg CO2"

    # Etapas
    id_etapa: str  # Ex: coleta_castanha_in_natura, limpeza_lavagem, analise_visao_computacional...
    
    # Registro
    evento: str
    usuario_responsavel: str
    dispositivo_origem: str = "Sistema Web"
    localizacao: str
    nivel_confiabilidade: float = 99.9

# ==========================================
# API FastAPI
# ==========================================
app = FastAPI(title="Supply Chain Castanha da Amazônia - V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain()

@app.post("/mine_event/", summary="Registra um novo evento produtivo")
def mine_event(evento_req: EventoCastanha):
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Consolidando os dados conforme o CSV
    record_data = evento_req.dict()
    record_data["id_registro"] = str(uuid.uuid4())
    record_data["timestamp_evento"] = time()
    record_data["status_validacao"] = "Validado"
    record_data["assinatura_digital"] = hashlib.sha256(str(record_data).encode()).hexdigest()
    
    block = blockchain.create_block(
        proof=proof, 
        previous_hash=previous_hash,
        record_data=record_data
    )
    
    # O código_blockchain e qr_code são referências ao hash do bloco na rede
    return {
        "message": "Evento minerado com sucesso!",
        "codigo_blockchain": block['hash_bloco'],
        "id_registro": record_data["id_registro"],
        "block": block
    }

@app.get("/chain/", summary="Visualiza toda a rede blockchain")
def get_chain():
    return {"chain": blockchain.chain, "length": len(blockchain.chain)}

@app.get("/produto/{id_produto}", summary="Busca o histórico e rastreabilidade de um produto/lote")
def get_product_history(id_produto: str):
    history = [b for b in blockchain.chain if b.get('dados_registro', {}).get('id_produto') == id_produto]
    if not history:
        raise HTTPException(status_code=404, detail="Produto não encontrado na blockchain.")
    return {"id_produto": id_produto, "history": history}