import os
import sys
import time
import shutil
import requests

# ========== CONSTANTES ==========
CAMINHO_PROJETO = "C:\\Users\\João Pedro\\Desktop\\VS Code - projects\\executavel"
CAMINHO_STATIC = os.path.join(CAMINHO_PROJETO, "static")
CAMINHO_SISTEMAS = os.path.join(CAMINHO_STATIC, "sistemas")
CAMINHO_OUTPUT = os.path.join(CAMINHO_PROJETO, "output")
URL_API = "http://localhost:5000/"

# ========== CONFIGURAÇÕES ==========
nome_do_arquivo_com_extensao = os.path.splitext(os.path.basename(__file__))
nome_do_arquivo = nome_do_arquivo_com_extensao[0]
tipo_de_arquivo = nome_do_arquivo_com_extensao[1]

#obter objeto do banco de dados
def get_objeto_banco(nome_sistema):
    try:
        response = requests.get(f'{URL_API}sistemas/', params={'nome': nome_sistema})
        if response.status_code == 200:
            dados = response.json()
            if isinstance(dados, list):
                if len(dados) > 0:
                    objeto_banco = dados[0]
                    return objeto_banco  # Retorna o objeto completo
                else:
                    print(f"Sistema '{nome_sistema}' não encontrado.")
                    return None
            else:
                print(f"Mais de 1 sistema com nome '{nome_sistema}' encontrado.")
                return None
        else:
            print(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")
        return None
  
objeto_banco = get_objeto_banco(nome_do_arquivo)
objeto_banco['version'] = str(objeto_banco['version'])
versoes_local = os.listdir(os.path.join(CAMINHO_SISTEMAS, objeto_banco['nome']))

def obter_versao_local(versoes_local):
    try:
        versoes_numericas = []
        
        for versao in versoes_local:
            try:
                versao = int(versao)
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

versao_atual = obter_versao_local(versoes_local)

def atualizar_sistema(objeto_banco):
    print(f"Iniciando processo de atualização do sistema...")
    try:
        if objeto_banco:
            diretorio_destino = os.path.join(CAMINHO_SISTEMAS, objeto_banco['nome'], objeto_banco['version'])
            print(f"Diretório de destino criado: {diretorio_destino}")
            
            if os.path.exists(diretorio_destino):
                print(f"Diretório já existe - versão {objeto_banco['version']} já foi baixada anteriormente")
                print(f"Processo concluído - versão {objeto_banco['version']} disponível")

            os.makedirs(diretorio_destino, exist_ok=True)

            arquivo_origem = objeto_banco['arquivo']
            
            #!USAR SOMENTE QUANDO VIRAR .EXE
            # arquivo_destino = os.path.join(objeto_banco['nome'], objeto_banco['version'], tipo_de_arquivo)
            #!USAR SOMENTE EM QUANTO FOR .PY
            arquivo_destino = nome_do_arquivo + objeto_banco['version'] + '.exe'
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
            
            print(f"Iniciando cópia do arquivo...")
            try:
                shutil.copy(arquivo_origem, destino_completo)
                print(f"Arquivo copiado com sucesso!")
                print(f"Nova versão {objeto_banco['version']} criada em: {diretorio_destino}")
                print(f"Iniciando execução da nova versão...")
                input("Aperte Enter para encerrar")
                fechar(objeto_banco)
            except Exception as copy_error:
                print(f"❌ Erro durante a cópia do arquivo:")
                print(f"❌ Detalhes: {copy_error}")
                print(f"❌ Origem: {arquivo_origem}")
                print(f"❌ Destino: {destino_completo}")
        else:
            print("❌ Nenhuma versão encontrada no banco de dados")
            print("❌ Verifique se há registros na tabela 'sistemas'")
    except Exception as e:
        print(f"❌ Erro durante o processo de atualização:")
        print(f"❌ Detalhes: {e}")
        print(f"❌ Possíveis causas: conexão com banco, permissões de arquivo, espaço em disco")
    
#fecha o arquivo que esta rodando e abre o novo
def fechar(objeto_banco):
            try:
                #!USAR SOMENTE QUANDO VIRAR .EXE
                # arquivo_executar = os.path.abspath(f"{CAMINHO_SISTEMAS}\\{objeto_banco['nome']}\\{objeto_banco['version']}\\{objeto_banco['nome']}{objeto_banco['version']}.{tipo_de_arquivo}")
                #!USAR SOMENTE EM QUANTO FOR .PY
                arquivo_executar = os.path.abspath(f"{CAMINHO_SISTEMAS}\\{objeto_banco['nome']}\\{objeto_banco['version']}\\{objeto_banco['nome']}{objeto_banco['version']}.exe")
                    
                if os.path.exists(arquivo_executar):
                    print(f"Iniciando: {arquivo_executar}")
                    os.startfile(arquivo_executar)
                    sys.exit(0)
            except Exception as E:
                print(f"❌ Erro durante a cópia do arquivo:")
                print(f"❌ Detalhes: {E}")

if __name__ == "__main__":
    print(f"Conteúdo da pasta: {versao_atual}")
    input("Aperte Enter para encerrar")

    if int(objeto_banco['version']) > int(versao_atual):
        input("Aperte Enter para encerrar")
        atualizar_sistema(objeto_banco)
    elif int(objeto_banco['version']) == int(versao_atual):
        print("Sistema já está na versão mais recente!")
        input("Aperte Enter para encerrar")
    else:
        print("Sistema já está na versão mais recente!")
        input("Aperte Enter para encerrar")