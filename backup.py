#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import subprocess
from datetime import datetime
from cryptography.fernet import Fernet
from typing import List, Optional

BACKUP_DIR = os.getenv('BACKUP_DIR', '/home/royal_green')
BACKUP_DEST = os.getenv('BACKUP_DEST', '/var/backups')
RCLONE_REMOTE = os.getenv('RCLONE_REMOTE', 'gdrive:backups')
MAX_BACKUPS = 5
KEY_FILE = os.path.join(BACKUP_DIR, 'backup.key')

logging.basicConfig(
    filename='/var/log/backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BackupManager:
    def __init__(self):
        self.fernet = self._initialize_encryption()
        self._ensure_directories()

    def _initialize_encryption(self) -> Fernet:
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as key_file:
                key_file.write(key)
            logging.info("Nova chave de criptografia gerada")
        else:
            with open(KEY_FILE, 'rb') as key_file:
                key = key_file.read()
        return Fernet(key)

    def _ensure_directories(self):
        os.makedirs(BACKUP_DEST, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _get_backup_filename(self) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f"backup_{timestamp}.tar.gz"

    def _get_exclude_patterns(self) -> List[str]:
        return [
            '/proc/*',
            '/sys/*',
            '/dev/*',
            '/tmp/*',
            '*.swp',
            '*.cache',
            '.*',
            '*.pyc',
            '__pycache__',
            '*.log'
        ]

    def create_backup(self) -> Optional[str]:
        try:
            backup_file = self._get_backup_filename()
            temp_backup = os.path.join(BACKUP_DEST, f"temp_{backup_file}")
            final_backup = os.path.join(BACKUP_DEST, backup_file)

            exclude_args = []
            for pattern in self._get_exclude_patterns():
                exclude_args.extend(['--exclude', pattern])

            tar_cmd = ['tar', '-czf', temp_backup] + exclude_args + [BACKUP_DIR]
            subprocess.run(tar_cmd, check=True)

            with open(temp_backup, 'rb') as f:
                data = f.read()
            encrypted_data = self.fernet.encrypt(data)
            with open(final_backup, 'wb') as f:
                f.write(encrypted_data)

            os.remove(temp_backup)
            logging.info(f"Backup criado com sucesso: {backup_file}")
            return backup_file

        except Exception as e:
            logging.error(f"Erro ao criar backup: {str(e)}")
            return None

    def upload_to_cloud(self, backup_file: str) -> bool:
        try:
            source = os.path.join(BACKUP_DEST, backup_file)
            cmd = ['rclone', 'copy', source, RCLONE_REMOTE]
            subprocess.run(cmd, check=True)
            logging.info(f"Backup enviado com sucesso para {RCLONE_REMOTE}")
            return True
        except Exception as e:
            logging.error(f"Erro ao enviar backup para nuvem: {str(e)}")
            return False

    def cleanup_old_backups(self):
        try:
            backups = sorted([
                f for f in os.listdir(BACKUP_DEST)
                if f.startswith('backup_') and f.endswith('.tar.gz')
            ])
            
            while len(backups) > MAX_BACKUPS:
                oldest_backup = backups.pop(0)
                os.remove(os.path.join(BACKUP_DEST, oldest_backup))
                logging.info(f"Backup antigo removido: {oldest_backup}")
        except Exception as e:
            logging.error(f"Erro ao limpar backups antigos: {str(e)}")

def main():
    try:
        backup_manager = BackupManager()
        backup_file = backup_manager.create_backup()
        
        if backup_file:
            if backup_manager.upload_to_cloud(backup_file):
                backup_manager.cleanup_old_backups()
                logging.info("Processo de backup concluído com sucesso")
            else:
                logging.error("Falha ao enviar backup para nuvem")
        else:
            logging.error("Falha ao criar backup")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Erro crítico durante o backup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 