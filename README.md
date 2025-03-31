# Script de Backup Automatizado

Este script Python realiza backups automatizados com as seguintes funcionalidades:
- Compactação de arquivos usando tar.gz
- Exclusão de arquivos e diretórios do sistema
- Criptografia AES-256
- Upload para serviço de nuvem via rclone
- Logging de operações
- Manutenção dos últimos 5 backups

## Requisitos

- Python 3.6 ou superior
- rclone instalado e configurado
- Permissões de escrita em /var/log e /var/backups

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure o rclone para seu serviço de nuvem preferido:
   ```bash
   rclone config
   ```

## Configuração

O script pode ser configurado através de variáveis de ambiente:

- `BACKUP_DIR`: Diretório a ser backup (padrão: /home/royal_green/Desktop/backup)
- `BACKUP_DEST`: Diretório de destino dos backups (padrão: /var/backups)
- `RCLONE_REMOTE`: Nome do remote rclone configurado (padrão: gdrive:backups)

## Uso

1. Torne o script executável:
   ```bash
   chmod +x backup.py
   ```

2. Execute o script:
   ```bash
   ./backup.py
   ```

## Agendamento com Cron

Para executar o backup diariamente às 02:00, adicione a seguinte linha ao crontab:

```bash
0 2 * * * /caminho/completo/para/backup.py
```

## Logs

Os logs são salvos em `/var/log/backup.log`

## Segurança

- A chave de criptografia é gerada automaticamente na primeira execução
- A chave é armazenada em `backup.key` no diretório de backup
- Mantenha a chave em local seguro e faça backup dela

## Tratamento de Erros

O script inclui tratamento de erros robusto e logging detalhado. Em caso de falha:
1. Verifique os logs em `/var/log/backup.log`
2. Certifique-se de que todas as dependências estão instaladas
3. Verifique as permissões dos diretórios
4. Confirme se o rclone está configurado corretamente 