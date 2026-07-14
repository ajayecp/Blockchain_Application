==============================================================================
   RASTREABILIDADE SUSTENTÁVEL NA INDÚSTRIA 5.0: UMA ABORDAGEM COM BLOCKCHAIN 
   SIMULADA NA CADEIA PRODUTIVA DA CASTANHA-DA-AMAZÔNIA
 =============================================================================

Alunos: Ajay Ramchandani
               Antonio Carlos de Castro Silva
               Ingrid Marina Pinto Pereira
Professor: Iury Valente de Bessa
Considerei o OS Windows usando o VS Code. 

O programa tem DUAS partes que funcionam juntas:
  1) O BACKEND (servidor) -> arquivo main.py.
  2) O FRONTEND (telas)   -> paginas que voce abre no navegador
                              (index.html e emulador.html).

o servidor (backend) precisa ficar LIGADO o tempo todo
enquanto voce usa as telas. Por isso vamos usar DOIS terminais:
  - Terminal 1 -> liga o servidor e fica rodando (nao feche!).
  - Terminal 2 -> abre as paginas do navegador.
  Para abrir o segundo terminal digite Ctrl+Shift+'


--------------------------------------------------------------------------
ANTES DE COMECAR (so na primeira vez)
--------------------------------------------------------------------------
1) Tenha o Git instalado: https://git-scm.com/ , após isso abra o VS Code ou IDE de sua preferencia,
abra o terminal e use o seguinte comando
        git clone https://github.com/ajayecp/Blockchain_Application

2) Tenha o Python instalado. Para conferir, abra o VS Code, va no menu
   superior em  Terminal > Novo Terminal  e digite:

       python --version

   Se aparecer algo como "Python 3.12.x", esta tudo certo. Se der erro,
   instale o Python pelo site oficial: https://www.python.org/downloads/
   (marque a opcao "Add Python to PATH" durante a instalacao).

3) Abra a PASTA do projeto no VS Code:
       Menu  Arquivo > Abrir Pasta...  e escolha a pasta:
       c:\Blockchain_Application

4)  Execute os seguintes comandos em um terminal para usar variáveis de ambiente e instalar dependencias
        python -m venv env ou
        py -3.14 -m venv env
        .\env\Scripts\activate
        pip install -r .\requirements.txt
==========================================================================
   PARTE 1 - LIGAR O SERVIDOR (BACKEND) A PARTIR DO main.py
==========================================================================

PASSO 1.1 - Abrir o primeiro terminal
   No VS Code, va no menu superior:
       Terminal > Novo Terminal
   Uma janela preta (terminal) vai aparecer na parte de baixo da tela.

PASSO 1.2 - Entrar na pasta do backend
   No terminal que abriu, digite a linha abaixo e aperte ENTER:

       cd c:\Blockchain_Application\backend-module

PASSO 1.3 - Ligar o servidor
   Agora digite a linha abaixo e aperte ENTER:

       .\venv\Scripts\uvicorn.exe main:app --reload

PASSO 1.4 - Confirmar que ligou
   Deu certo se aparecerem mensagens parecidas com estas:

       INFO:  Started server process [.....]
       INFO:  Waiting for application startup.
       INFO:  Application startup complete.
       INFO:  Uvicorn running on http://127.0.0.1:8000

   O servidor esta no ar no endereco:  http://127.0.0.1:8000

   >>> IMPORTANTE: NAO FECHE ESTE TERMINAL. <<<
   Ele precisa continuar rodando enquanto voce usa o programa.
   
   Para testar a API diretamente, abra no navegador:
       http://127.0.0.1:8000/docs


==========================================================================
   PARTE 2 - ABRIR AS TELAS (FRONTEND) PELO SEGUNDO TERMINAL
==========================================================================

PASSO 2.1 - Abrir um SEGUNDO terminal
   No VS Code, no canto do painel do terminal, clique no sinal de "+"
   (Novo Terminal). Ou use o menu:  Terminal > Novo Terminal. Ou digite Ctrl+Shift+'
   Vai abrir uma nova aba de terminal (o primeiro continua rodando).

PASSO 2.2 - Abrir a tela principal (Cadastro e Rastreabilidade)
   Neste segundo terminal, digite e aperte ENTER:

    python -m http.server 8080
   A pagina vai abrir no seu navegador padrao (Chrome, Edge, etc.).


==========================================================================
   PARTE 3 - COMO USAR O PROGRAMA (AS TELAS)
==========================================================================

Voce tem 3 telas:

  [A] index.html  -> CADASTRO + RASTREABILIDADE
      * Em cima: preencha os dados do lote e clique em
        "REGISTRAR NA BLOCKCHAIN" para gravar um evento.
        (Campos obrigatorios: ID Produto e Descricao do Evento.)
      * Embaixo: digite o ID de um lote e clique em
        "BUSCAR HISTORICO COMPLETO" para ver toda a trajetoria dele.

  [B] emulador.html -> GERADOR DE DADOS PARA TESTE
      * Escolha a quantidade de lotes (ex.: 5) e clique em
        "GERAR E MINERAR NA BLOCKCHAIN". Ele cria varios lotes de
        exemplo automaticamente. Use a "Semente" 42 para sempre gerar
        os mesmos dados.

  [C] http://127.0.0.1:8000/docs -> TELA DE TESTE DA API (Swagger)
      * Permite testar cada funcao do servidor diretamente.

ROTEIRO SUGERIDO PARA VER TUDO FUNCIONANDO:
   1. Abra o emulador.html e gere 5 lotes (semente 42).
   2. Copie um dos IDs de lote que aparecerem na tela.
   3. Abra o index.html, cole esse ID na parte de baixo e clique em
      "BUSCAR HISTORICO COMPLETO".
   4. Veja o historico completo do lote aparecer na tela.

OBS: tudo o que voce registrar fica salvo no arquivo:
   backend-module\blockchain_data.json
Por isso os dados continuam la mesmo se voce desligar e ligar de novo.


==========================================================================
   PARTE 4 - COMO DESLIGAR O PROGRAMA
==========================================================================

1) Feche as abas do navegador (as telas).
2) Volte ao PRIMEIRO terminal (o do servidor) e aperte as teclas:
       CTRL + C
   Isso desliga o servidor. Pode fechar o VS Code em seguida.


==========================================================================
   SOLUCAO DE PROBLEMAS (se algo der errado)
==========================================================================

PROBLEMA: Ao ligar o servidor aparece um erro de "execution policy"
   (algo sobre scripts desabilitados ao usar "Activate").
SOLUCAO: O comando do PASSO 1.3 usa o uvicorn.exe direto e NAO precisa
   ativar nada, entao normalmente nao da esse erro. Se mesmo assim
   precisar ativar o ambiente, rode antes:
       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

PROBLEMA: Os botoes das telas mostram "Erro" ou "falha na conexao".
CAUSA: O servidor (Parte 1) nao esta ligado, ou o primeiro terminal foi
   fechado. SOLUCAO: Volte a Parte 1 e ligue o servidor de novo. Deixe o
   terminal aberto.

PROBLEMA: "uvicorn.exe nao foi encontrado" ou erro parecido.
CAUSA: Voce nao esta na pasta certa. SOLUCAO: Confira que rodou o
   comando "cd ...backend-module" do PASSO 1.2 antes do PASSO 1.3.

PROBLEMA: Falta instalar as dependencias (ambiente novo / outro PC).
SOLUCAO: Na pasta backend-module, crie o ambiente e instale tudo:
       cd c:\AplicaoesInteligenciacyber\Blockchain_Application\backend-module
       python -m venv venv
       .\venv\Scripts\python.exe -m pip install -r requirements.txt
   Depois siga normalmente a Parte 1.

PROBLEMA: A porta 8000 ja esta em uso.
SOLUCAO: Ligue o servidor em outra porta, por exemplo 8001:
       .\venv\Scripts\uvicorn.exe main:app --reload --port 8001
   (Atencao: se mudar a porta, as telas que apontam para 8000 nao vao
   conectar. Use a porta 8000 sempre que possivel.)

--------------------------------------------------------------------------
Resumo rapido (decoreba):
   Terminal 1:  cd ...\backend-module
                .\venv\Scripts\uvicorn.exe main:app --reload      (deixe aberto)
   Terminal 2:  python -m http.server 8080
==========================================================================
