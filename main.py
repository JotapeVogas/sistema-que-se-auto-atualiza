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

def get_objeto_banco(versao_local):
    try:
        with Database() as banco:
            objeto_banco = banco.query(SistemaDB).order_by(SistemaDB.version.desc()).first()
            if objeto_banco:
                return objeto_banco
            else:
                print(f"Nenhuma versão maior que {versao_local} encontrada no banco")
                print(f"Sistema já está atualizado com a versão mais recente")
                return None
                
    except Exception as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
        print(f"❌ Verifique: conexão, credenciais e se a tabela 'sistemas' existe")
        return None

def atualizar_sistema():
    print(f"Iniciando processo de atualização do sistema...")
    
    try:
        objeto_banco = get_objeto_banco(versao_local)

        if objeto_banco:
            diretorio_destino = f"C:\\Users\\João Pedro\\Desktop\\VS Code - projects\\executavel\\static\\sistemas\\main\\{objeto_banco.version}"
            print(f"Diretório de destino criado: {diretorio_destino}")
            
            if os.path.exists(diretorio_destino):
                print(f"Diretório já existe - versão {objeto_banco.version} já foi baixada anteriormente")
                print(f"Processo concluído - versão {objeto_banco.version} disponível")
                return objeto_banco

            os.makedirs(diretorio_destino, exist_ok=True)

            arquivo_origem = objeto_banco.arquivo
            arquivo_destino = f'main{objeto_banco.version}.exe'
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
                print(f"Nova versão {objeto_banco.version} criada em: {diretorio_destino}")
                print(f"Iniciando execução da nova versão...")
                fechar(objeto_banco)
                return objeto_banco
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
    
def fechar(objeto_banco):
    print(f"\nOperação concluída! Nova versão {objeto_banco.version} criada.")
    print(f"Fechando em 10 segundos...")
    for i in range(9, 0, -1):
        print(f"Fechando em {i}...")
        time.sleep(1)

    arquivo_executar = os.path.abspath(f"./static/sistemas/main/{objeto_banco.version}/main{objeto_banco.version}.exe")
    
    if os.path.exists(arquivo_executar):
        print(f"Iniciando: {arquivo_executar}")
        os.startfile(arquivo_executar)

        sys.exit(0)
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_executar}")

def get_caminho_executavel():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def obter_versao_local():
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

if __name__ == "__main__":
    versao_local = obter_versao_local()
    conteudo = os.listdir('./static/sistemas/main/')
    print(f"Conteúdo da pasta: {conteudo}")
    input("Aperte Enter para encerrar")
    objeto_banco = get_objeto_banco(versao_local)
    input("Aperte Enter para encerrar")

    if objeto_banco.version > versao_local:
        atualizar_sistema()
        print("Sistema atualizado com sucesso!")
        fechar(objeto_banco)
    else:
        print("Sistema já está na versão mais recente!")
        input("Aperte Enter para encerrar")