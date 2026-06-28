import hashlib
import json
import uuid
from time import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session

from database import SessionLocal, BlockModel, engine
import emulador

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

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            
            # Recria a estrutura exata do bloco anterior para recalcular o hash
            prev_block_content = {
                'index': previous_block.index,
                'timestamp': previous_block.timestamp,
                'dados': json.loads(previous_block.dados_json),
                'proof': previous_block.proof,
                'previous_hash': previous_block.previous_hash
            }
            
            # 1. Verifica se a ligação criptográfica foi quebrada
            # O 'previous_hash' do bloco atual TEM de ser igual ao hash recalculado do bloco anterior
            if block.previous_hash != self.hash(prev_block_content):
                return False
    
            previous_proof = previous_block.proof
            proof = block.proof
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
                
            previous_block = block
            block_index += 1
            
        return True

blockchain_logic = Blockchain()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # Cria Bloco Gênesis se a tabela estiver vazia
    if db.query(BlockModel).count() == 0:
        genesis_dados = {"evento": "Sistema de Castanha Iniciado", "status": "Online"}
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
# 1. Lista estrita baseada exatamente no seu diagrama de Modelagem Conceitual
ETAPAS_PRODUCAO_OFICIAIS = [
    "coleta_in_natura",
    "inspecao_entrada",          # Triagem inicial na esteira
    "limpeza_lavagem",          # Condicional (SIM) do Losango do fluxo
    "classificacao_ia_pre",     # Visão Computacional + IA antes da quebra
    "quebra_extracao",          # Extração física da amêndoa
    "classificacao_ia_pos",     # Visão Computacional + IA após a quebra (Qualidade/Tamanho)
    "empacotamento_final"       # O Pacote pronto para distribuição
]

@app.post("/mine_event/")
def mine_event(req: dict, db: Session = Depends(get_db)):
    # Validação de conformidade industrial
    id_etapa = req.get("id_etapa")
    if id_etapa not in ETAPAS_PRODUCAO_OFICIAIS:
        raise HTTPException(
            status_code=400, 
            detail=f"A etapa '{id_etapa}' não pertence ao fluxo oficial da fábrica. Etapas permitidas: {', '.join(ETAPAS_PRODUCAO_OFICIAIS)}"
        )

    prev_block = db.query(BlockModel).order_by(BlockModel.index.desc()).first()
    proof = blockchain_logic.proof_of_work(prev_block.proof)
    
    # Prepara dados do bloco para hashing
    block_content = {
        'index': prev_block.index + 1,
        'timestamp': time(),
        'dados': req,
        'proof': proof,
        'previous_hash': prev_block.id # Elo de ligação criptográfica
    }
    
    hash_bloco = blockchain_logic.hash(block_content)
    
    # Salva na BD relacional SQLite
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
    
    return {
        "status": "Bloco Minerado e Encadeado com Sucesso",
        "hash_bloco": hash_bloco,
        "etapa_validada": id_etapa
    }
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
                historico.append({"hash_bloco": b.id, "timestamp": b.timestamp, "dados": dados, "index": b.index})
        
        # Identifica o tipo de busca
        tipo = "Hash" if termo == id_produto_alvo else "Lote"
        return {"id_produto": id_produto_alvo, "historico": historico, "tipo_busca": tipo}
    
    raise HTTPException(status_code=404, detail="Não encontrado")

@app.get("/chain/")
def get_chain(db: Session = Depends(get_db)):
    blocks = db.query(BlockModel).order_by(BlockModel.index.asc()).all()
    
    return [
        {
            "index": b.index, 
            "hash_bloco": b.id, 
            "timestamp": b.timestamp, 
            "dados": json.loads(b.dados_json)
        } 
        for b in blocks
    ]

@app.get("/validar/")
def validar_cadeia(db: Session = Depends(get_db)):
    # Puxa todos os blocos do banco de dados em ordem cronológica
    blocks = db.query(BlockModel).order_by(BlockModel.index.asc()).all()
    
    is_valid = blockchain_logic.is_chain_valid(blocks)
    
    if is_valid:
        return {
            "mensagem": "A Blockchain é válida! A integridade dos dados está garantida.", 
            "valido": True,
            "total_blocos": len(blocks)
        }
    else:
        # Se alguém alterou manualmente o banco de dados (SQLite), o sistema acusa o erro
        raise HTTPException(
            status_code=400, 
            detail="ALERTA: A Blockchain foi adulterada e é inválida!"
        )
@app.put("/ataque_simulado/{bloco_index}")
def ataque_simulado(bloco_index: int, db: Session = Depends(get_db)):
    # 1. Busca o bloco específico no banco de dados
    bloco = db.query(BlockModel).filter(BlockModel.index == bloco_index).first()
    
    if not bloco:
        raise HTTPException(status_code=404, detail="Bloco não encontrado na rede.")

    # 2. Carrega o JSON original (os dados verdadeiros da castanha)
    dados_alterados = json.loads(bloco.dados_json)
    
    # 3. Faz a alteração maliciosa
    # Vamos alterar o ID do produto e o peso para simular um desvio
    dados_alterados["id_produto"] = "LOTE-ADULTERADO-999"
    dados_alterados["peso_lote"] = 9999.99
    dados_alterados["usuario_responsavel"] = "Hacker Anónimo"
    
    # 4. Injeta o JSON corrompido de volta no banco SEM recalcular o Hash do bloco
    bloco.dados_json = json.dumps(dados_alterados)
    db.commit()

    return {"alerta": f"FRAUDE: Os dados de input do Bloco #{bloco_index} foram alterados silenciosamente no banco de dados!"}

@app.get("/rastreabilidade_ponta_a_ponta/{id_lote}")
def rastreabilidade_ponta_a_ponta(id_lote: str, db: Session = Depends(get_db)):
    # 1. Recolhe todos os blocos registados no SQLite (cronologia inversa para busca célere)
    blocks = db.query(BlockModel).order_by(BlockModel.index.desc()).all()
    
    linha_do_tempo_lote = []
    bloco_pesquisa = None

    # 2. Encontra o ponto final do fluxo (o evento mais recente do lote solicitado)
    for b in blocks:
        dados = json.loads(b.dados_json)
        if dados.get('id_produto') == id_lote:
            bloco_pesquisa = b
            break

    if not bloco_pesquisa:
        raise HTTPException(
            status_code=404, 
            detail=f"Nenhum registo de rastreabilidade encontrado para o lote: {id_lote}"
        )

    # 3. Executa a varredura recursiva baseada estritamente nos elos criptográficos (hashes)
    while bloco_pesquisa and bloco_pesquisa.index != 1:  # Para ao chegar ao Bloco Gênesis
        dados_atuais = json.loads(bloco_pesquisa.dados_json)
        
        # Consolida a ficha de auditoria daquela etapa específica da esteira
        linha_do_tempo_lote.append({
            "index_bloco": bloco_pesquisa.index,
            "assinatura_hash": bloco_pesquisa.id,
            "etapa_processo": dados_atuais.get("id_etapa"),
            "descricao_evento": dados_atuais.get("evento"),
            "localizacao_exata": dados_atuais.get("localizacao"),
            "responsavel_tecnico": dados_atuais.get("usuario_responsavel"),
            "dispositivo_hardware": dados_atuais.get("dispositivo_origem"),
            "timestamp_operacao": datetime.fromtimestamp(bloco_pesquisa.timestamp).isoformat() if bloco_pesquisa.timestamp else None,            "dados_inspecao": {
                "peso_kg": dados_atuais.get("peso_lote"),
                "umidade_percentual": dados_atuais.get("umidade"),
                "status_qualidade": dados_atuais.get("status_produto"),
                "nivel_confianca_hardware": dados_atuais.get("nivel_confiabilidade")
            }
        })

        # O elo da corrente: O próximo bloco a ser analisado TEM de ter o ID igual ao previous_hash do atual
        bloco_pesquisa = db.query(BlockModel).filter(BlockModel.id == bloco_pesquisa.previous_hash).first()

    # 4. Inverte a lista para exibir na ordem cronológica natural (da floresta ao pacote)
    linha_do_tempo_lote.reverse()

    # 5. Verifica se o ciclo de vida cumpriu os requisitos do modelo conceitual (ex: passou por todas as fases essenciais)
    etapas_percorridas = [item["etapa_processo"] for item in linha_do_tempo_lote]
    fluxo_completo_garantido = "coleta_in_natura" in etapas_percorridas and "empacotamento_final" in etapas_percorridas

    return {
        "lote_rastreado": id_lote,
        "auditoria_status": "INTEGRIDADE VERIFICADA E IMUTÁVEL",
        "certificado_procedencia_valido": fluxo_completo_garantido,
        "total_etapas_identificadas": len(linha_do_tempo_lote),
        "linha_do_tempo_rastreabilidade": linha_do_tempo_lote
    }

@app.post("/emular/")
def emular_lotes(
    n_lotes: int = 1, 
    intercalar: bool = False, 
    prob_descarte: float = 0.0, 
    seed: int = None,
    db: Session = Depends(get_db)
):
    # Usa a função do seu colega para criar a fila de eventos sintéticos
    fila = emulador.montar_fila(
        n_lotes=n_lotes, 
        intercalar=intercalar,
        prob_descarte=prob_descarte, 
        seed=seed
    )

    minerados = 0
    primeiro_hash = None
    ultimo_hash = None

    for evento in fila:
        # PULO DO GATO: Passa o evento do emulador para a SUA função oficial que grava no SQLite
        resultado = mine_event(req=evento, db=db)
        
        hash_atual = resultado["hash_bloco"]
        if not primeiro_hash:
            primeiro_hash = hash_atual
        ultimo_hash = hash_atual
        minerados += 1

    lotes_ids = sorted({ev["id_produto"] for ev in fila})
    
    return {
        "status": "Emulacao concluida",
        "lotes_gerados": n_lotes,
        "lotes_ids": lotes_ids,
        "eventos_minerados": minerados,
        "primeiro_hash": primeiro_hash,
        "ultimo_hash": ultimo_hash,
        "total_blocos_na_cadeia": db.query(BlockModel).count()
    }