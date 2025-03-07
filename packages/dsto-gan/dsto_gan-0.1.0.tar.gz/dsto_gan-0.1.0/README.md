DSTO-GAN: Balanceamento de Dados com GAN
O DSTO-GAN é uma biblioteca Python que utiliza uma Rede Generativa Adversarial (GAN) para gerar amostras sintéticas e balancear datasets desbalanceados. Ele é especialmente útil para problemas de classificação em que as classes estão desproporcionais.

Funcionalidades
1. Geração de amostras sintéticas para balanceamento de classes.
2. Treinamento de um GAN personalizado para dados tabulares.
3. Salvamento do dataset balanceado em um arquivo .csv.

Pré-requisitos
Python 3.6 ou superior.

Gerenciador de pacotes pip.

Instalação das Dependências
As dependências serão instaladas automaticamente na primeira execução. Caso prefira instalar manualmente, execute:

pip install numpy torch pandas scikit-learn4

Como Usar

1. Preparação do Arquivo de Dados
O arquivo de entrada deve ser um .csv com a seguinte estrutura:
A última coluna deve ser nomeada como class e conter os rótulos das classes.
As demais colunas devem conter as features (atributos) do dataset.

Exemplo de arquivo desbalanceado.csv:

feature1,feature2,feature3,class
1.2,3.4,5.6,0
2.3,4.5,6.7,1
3.4,5.6,7.8,0

2. Execução do Código
Salve o código em um arquivo Python, por exemplo: gerar_balanceado.py.

Execute o código no terminal:

python gerar_balanceado.py

Durante a execução:

O programa solicitará o caminho do arquivo .csv de entrada.

Exemplo: C:/dados/desbalanceado.csv

Em seguida, solicitará o caminho para salvar o arquivo .csv balanceado.

Exemplo: C:/dados/balanceado.csv

3. Resultado
Após a execução, o programa gerará um arquivo .csv balanceado no caminho especificado.

O arquivo de saída terá a mesma estrutura do arquivo de entrada, mas com as classes balanceadas.

Exemplo de Uso
Passo a Passo
Prepare o arquivo desbalanceado.csv com a estrutura correta.

Execute o código:
python gerar_balanceado.py
Forneça os caminhos:

Digite o caminho do arquivo .csv de entrada: C:/dados/desbalanceado.csv
Digite o caminho do arquivo .csv de saída: C:/dados/balanceado.csv
Verifique o arquivo balanceado.csv gerado.

Estrutura do Projeto
dsto_gan/
│
├── dsto_gan.py          # Código principal para balanceamento de dados
├── README.md            # Documentação do projeto
└── requirements.txt     # Dependências do projeto (opcional)

Solução de Problemas
Erro ao Ler o Arquivo
Verifique se o caminho do arquivo está correto.

Certifique-se de que o arquivo está no formato .csv e segue a estrutura esperada.

Erro de Instalação de Bibliotecas
Certifique-se de que o pip está instalado e atualizado.

Execute manualmente a instalação das bibliotecas:

pip install numpy torch pandas scikit-learn
Erro Durante a Execução
Verifique se o arquivo de entrada contém uma coluna chamada class.

Certifique-se de que todas as colunas, exceto class, contêm valores numéricos.

Contribuição
Contribuições são bem-vindas! Siga os passos abaixo:

Faça um fork do repositório.

Crie uma branch para sua feature (git checkout -b feature/nova-feature).

Commit suas mudanças (git commit -m 'Adicionando nova feature').

Faça push para a branch (git push origin feature/nova-feature).

Abra um Pull Request.

Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

Contato
Autor: Erika Assis

Email: dudabh@gmail.com

Repositório: GitHub

Agradecimentos
Este projeto foi desenvolvido como parte de uma pesquisa em balanceamento de dados usando GANs.

Agradecimentos à comunidade de código aberto por fornecer as bibliotecas utilizadas.


