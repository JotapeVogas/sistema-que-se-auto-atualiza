from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import sys
import time
import shutil

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
Database = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo da tabela sistemas
class SistemaDB(Base):
    __tablename__ = 'sistemas'
    
    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)
    arquivo = Column(String, nullable=False)
    nome = Column(String, nullable=True)


conteudo = os.listdir('./static/sistemas/main/')
print(f"Conteúdo da pasta: {conteudo}")

def verificar_versao_atual_banco(versao_local):
    print(f"Consultando banco de dados para versões maiores que: {versao_local}")
    
    try:
        with Database() as banco:
            sistema_banco = banco.execute(
                select(SistemaDB.version, SistemaDB.arquivo)
                .order_by(SistemaDB.version.desc())
                .limit(1)
            ).fetchone()

            if sistema_banco:
                print(f"Versão mais recente encontrada no banco: {sistema_banco.version}")
                print(f"Iniciando processo de atualização...")
                atualizar_sistema()
                return True
            else:
                print(f"Nenhuma versão maior que {versao_local} encontrada no banco")
                print(f"Sistema já está atualizado com a versão mais recente")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
        print(f"❌ Verifique: conexão, credenciais e se a tabela 'sistemas' existe")
        return False

def atualizar_sistema():
    print(f"Iniciando processo de atualização do sistema...")
    
    try:
        with Database() as banco:
            print(f"Buscando versão mais recente no banco de dados...")
            sistema_banco = banco.execute(
                select(SistemaDB.version, SistemaDB.arquivo)
                .order_by(SistemaDB.version.desc())
                .limit(1)
            ).fetchone()

            if sistema_banco:
                versao_banco = sistema_banco.version
                print(f"Versão encontrada no banco: {versao_banco}")
                
                diretorio_destino = f"./static/sistemas/main/{versao_banco}"
                print(f"Diretório de destino criado: {diretorio_destino}")
                
                if os.path.exists(diretorio_destino):
                    print(f"Diretório já existe - versão {versao_banco} já foi baixada anteriormente")
                    print(f"Processo concluído - versão {versao_banco} disponível")
                    return versao_banco
                
                print(f"Criando diretório: {diretorio_destino}")
                os.makedirs(diretorio_destino, exist_ok=True)
                
                arquivo_origem = './output/main.exe'
                arquivo_destino = f'main{versao_banco}.exe'
                destino_completo = os.path.join(diretorio_destino, arquivo_destino)
                
                print(f"Verificando arquivo de origem: {arquivo_origem}")
                print(f"Destino final: {destino_completo}")
                
                if not os.path.exists(arquivo_origem):
                    print(f"❌ Arquivo de origem não encontrado: {arquivo_origem}")
                    print(f"Conteúdo da pasta output:")
                    if os.path.exists('./output'):
                        conteudo_output = os.listdir('./output')
                        for item in conteudo_output:
                            print(f"   - {item}")
                    else:
                        print("❌ Pasta './output' não existe")
                    return None
                
                print(f"Iniciando cópia do arquivo...")
                try:
                    shutil.copy(arquivo_origem, destino_completo)
                    print(f"Arquivo copiado com sucesso!")
                    print(f"Nova versão {versao_banco} criada em: {diretorio_destino}")
                    print(f"Iniciando execução da nova versão...")
                    fechar(versao_banco)
                    return versao_banco
                except Exception as copy_error:
                    print(f"❌ Erro durante a cópia do arquivo:")
                    print(f"❌ Detalhes: {copy_error}")
                    print(f"❌ Origem: {arquivo_origem}")
                    print(f"❌ Destino: {destino_completo}")
                    return None
            else:
                print("❌ Nenhuma versão encontrada no banco de dados")
                print("❌ Verifique se há registros na tabela 'sistemas'")
                return None
    except Exception as e:
        print(f"❌ Erro durante o processo de atualização:")
        print(f"❌ Detalhes: {e}")
        print(f"❌ Possíveis causas: conexão com banco, permissões de arquivo, espaço em disco")
        return None

def fechar(versao_nova):
    print(f"\nOperação concluída! Nova versão {versao_nova} criada.")
    print("Abrindo em 10 segundos...")
    time.sleep(10)
    
    arquivo_executar = os.path.abspath(f"./static/sistemas/main/{versao_nova}/main{versao_nova}.exe")
    
    if os.path.exists(arquivo_executar):
        print(f"Iniciando: {arquivo_executar}")
        os.startfile(arquivo_executar)
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_executar}")
    
    sys.exit(0)

def get_caminho_executavel():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def obter_versao_atual_local():
    try:
        conteudo = os.listdir('./static/sistemas/main/')
        versoes_numericas = []
        
        for item in conteudo:
            try:
                versao = int(item)
                versoes_numericas.append(versao)
            except ValueError:
                continue
        
        if versoes_numericas:
            versao_mais_recente = max(versoes_numericas)
            print(f"Versão mais recente local encontrada: {versao_mais_recente}")
            return versao_mais_recente
        else:
            print("❌ Nenhuma versão válida encontrada localmente")
            return 0
            
    except FileNotFoundError:
        print("❌ Pasta ./static/sistemas/main/ não encontrada")
        return 0

versao_atual = obter_versao_atual_local()
alterar = verificar_versao_atual_banco(versao_atual)

if alterar:
    print("Sistema atualizado com sucesso!")
else:
    print("Sistema já está na versão mais recente!")
    input("Aperte Enter para encerrar")