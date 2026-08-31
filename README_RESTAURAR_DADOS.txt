CORREÇÃO PARA RESTAURAR OS DADOS NO COOLIFY

O sistema criou dois volumes porque o docker-compose novo usava outro nome/caminho de volume.
O volume antigo que aparece no Coolify como *_mecanica-jairo-data provavelmente contém os dados antigos.
Este pacote aponta novamente o sistema para esse volume antigo.

Passos:
1. Não delete nenhum volume no Coolify.
2. Suba estes arquivos no GitHub substituindo os anteriores.
3. No Coolify, deixe Docker Compose Location como /docker-compose.yml.
4. Clique em Save.
5. Clique em Reload Compose File.
6. Clique em Force Redeploy.
7. Confira se os clientes, OS e estoque voltaram.

Depois que confirmar que está tudo certo, deixe o outro volume vazio quieto por alguns dias.
Não apague antes de ter certeza.


CORREÇÃO FINAL DO BANCO
=======================
Pelo terminal do Coolify, o banco com dados é:
/data/oficina.db  (772K)

O banco vazio era:
/data/jairo_oficina.db  (4K)

Este pacote aponta o sistema para DB_PATH=/data/oficina.db e mantém o volume mecanica-jairo-data montado em /data.

ANTES DO REDEPLOY, no terminal do container, rode por segurança:
cp /data/oficina.db /data/oficina.db.backup_antes_dbpath_$(date +%Y%m%d_%H%M%S)

Depois suba estes arquivos no GitHub, Reload Compose File e Force Redeploy.
Não apague nenhum volume até conferir clientes, OS e estoque.
