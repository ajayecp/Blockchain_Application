import hashlib
import json
import uuid
from time import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importamos a nossa nova estrutura de base de dados
from database import SessionLocal, BlockModel, engine

# Função para obter a sessão da BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Blockchain:
    def hash(self, block_data):
        encoded_block = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_op[:4] == '0000': return new_proof
            new_proof += 1

blockchain_logic = Blockchain()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # Cria Bloco Gênesis se a tabela estiver vazia
    if db.query(BlockModel).count() == 0:
        genesis_dados = {"evento": "Gênesis - Sistema de Castanha Iniciado", "status": "Online"}
        block_data = {
            'index': 1,
            'timestamp': time(),
            'dados': genesis_dados,
            'proof': 100,
            'previous_hash': '1'
        }
        hash_val = blockchain_logic.hash(block_data)
        db_block = BlockModel(
            id=hash_val,
            index=1,
            timestamp=block_data['timestamp'],
            proof=100,
            previous_hash='1',
            dados_json=json.dumps(genesis_dados)
        )
        db.add(db_block)
        db.commit()
    db.close()

@app.post("/mine_event/")
def mine_event(req: dict, db: Session = Depends(get_db)):
    prev_block = db.query(BlockModel).order_by(BlockModel.index.desc()).first()
    proof = blockchain_logic.proof_of_work(prev_block.proof)
    
    # Prepara dados do bloco para hashing
    block_content = {
        'index': prev_block.index + 1,
        'timestamp': time(),
        'dados': req,
        'proof': proof,
        'previous_hash': prev_block.id
    }
    
    hash_bloco = blockchain_logic.hash(block_content)
    
    # Salva na BD
    new_block = BlockModel(
        id=hash_bloco,
        index=block_content['index'],
        timestamp=block_content['timestamp'],
        proof=proof,
        previous_hash=prev_block.id,
        dados_json=json.dumps(req)
    )
    db.add(new_block)
    db.commit()
    
    return {"codigo_blockchain": hash_bloco}
@app.get("/buscar/{termo}")
def buscar(termo: str, db: Session = Depends(get_db)):
    # Busca por Hash ou por ID do Produto dentro do JSON
    blocks = db.query(BlockModel).all()
    historico = []
    id_produto_alvo = None

    for b in blocks:
        dados = json.loads(b.dados_json)
        if b.id == termo or dados.get('id_produto') == termo:
            id_produto_alvo = dados.get('id_produto')
            break
    
    if id_produto_alvo:
        for b in blocks:
            dados = json.loads(b.dados_json)
            if dados.get('id_produto') == id_produto_alvo:
                # CORREÇÃO: Adicionamos o timestamp para a data funcionar
                historico.append({"hash_bloco": b.id, "timestamp": b.timestamp, "dados": dados, "index": b.index})
        
        # Identifica o tipo de busca
        tipo = "Hash" if termo == id_produto_alvo else "Lote"
        return {"id_produto": id_produto_alvo, "historico": historico, "tipo_busca": tipo}
    
    raise HTTPException(status_code=404, detail="Não encontrado")

@app.get("/chain/")
def get_chain(db: Session = Depends(get_db)):
    blocks = db.query(BlockModel).order_by(BlockModel.index.asc()).all()
    
    # CORREÇÃO: Mudámos de "hash" para "hash_bloco" e adicionámos o "timestamp"
    return [
        {
            "index": b.index, 
            "hash_bloco": b.id, 
            "timestamp": b.timestamp, 
            "dados": json.loads(b.dados_json)
        } 
        for b in blocks
    ]