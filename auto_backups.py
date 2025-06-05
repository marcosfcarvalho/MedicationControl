import os
import shutil
import subprocess
from datetime import datetime

def executar_backup_pelo_python():
    # Data no formato YYYY-MM-DD
    data = datetime.now().strftime("%Y-%m-%d")

    # Caminho do banco original
    origem = os.path.abspath("controle_medicamentos.db")

    # Nome do arquivo temporário com a data
    arquivo_temp = os.path.abspath(f"controle_medicamentos_{data}.db")

    try:
        # Copia o banco com a data no nome
        shutil.copyfile(origem, arquivo_temp)

        print("⏳ Enviando para o Google Drive com rclone...")

        # Envia para o Google Drive usando rclone
        subprocess.run([
            "rclone", "copy", "--progress",
            arquivo_temp, "gdrive_enf:", "--exclude=/.tmp.driveupload**"  #troque o nome "gdrive_enf:" pelo seu remote rclone ou crie um remote rclone com o mesmo nome
        ], check=True)

        print("✅ Backup enviado com sucesso.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o rclone: {e}")
    except Exception as e:
        print(f"❌ Erro geral durante o backup: {e}")
    finally:
        # Tenta apagar o arquivo temporário
        try:
            os.remove(arquivo_temp)
            print("🗑️ Arquivo temporário removido.")
        except Exception as e:
            print(f"⚠️ Não foi possível remover o arquivo temporário: {e}")
