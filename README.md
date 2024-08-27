# GitHub self-hosted runners na AWS
Este script automatiza a criação de runners do GitHub em EC2 na AWS, proporcionando escalabilidade para seus workflows do GitHub Actions.

## Configuração Inicial

1. Crie uma instância EC2 e configure o runner: Siga as instruções em https://docs.github.com/pt/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners para configurar o runner na instância.
2. Crie uma AMI: Após a configuração, crie uma AMI (Amazon Machine Image) a partir da instância.
3. Crie um Launch Template: Utilize um Launch Template para provisionar as instâncias EC2 de forma consistente.
4. Crie uma função Lambda: Crie uma função Lambda com Runtime Python 3.12 e habilite o Function URL com "Auth Type=None".
5. Faça o deploy do código "main.py": Faça o deploy do código "main.py" na função Lambda, certificando-se de alterar os seguintes campos:
- **SECRET_KEY:** Defina uma chave secreta forte.
- **LAUNCH_TEMPLATE_ID:** Substitua pelo ID do seu Launch Template.
- **MIN_INSTANCES:** Defina a quantidade mínima de instâncias.
- **MAX_INSTANCES:** Defina a quantidade máxima de instâncias.

## Configuração do Webhook no GitHub

1. Acesse as configurações do repositório: No GitHub, vá até as configurações do repositório e clique em "Webhooks".
2. Adicione um webhook: Clique em "Add webhook" e preencha os seguintes campos:
- **Payload URL:** Adicione o URL Endpoint da função Lambda.
- **Content type:** application/json
- **Secret:** Insira a mesma senha definida no código Python no parâmetro SECRET_KEY.
- **SSL verification:** Desative temporariamente.
3. Selecione eventos: Em "Which events would you like to trigger this webhook", selecione "Let me select individual events" e marque apenas "Workflow jobs".

## Execução

Execute a pipeline e o script se encarregará de dimensionar automaticamente os runners em EC2 conforme a demanda dos seus workflows.

## Observações

Certifique-se de que a função Lambda tenha as permissões necessárias para criar e gerenciar instâncias EC2.
Ative a verificação SSL assim que possível para garantir a segurança da comunicação entre o GitHub e a função Lambda.
Monitore o dimensionamento dos runners e ajuste os parâmetros MIN_INSTANCES e MAX_INSTANCES conforme necessário.
Com este script, você terá um ambiente de CI/CD mais escalável e eficiente, garantindo que seus workflows do GitHub Actions sejam executados sem atrasos.
