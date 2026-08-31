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
