# GaiaSenses 

## O que é?

O projeto GaiaSenses propõe o desenvolvimento de um aplicativo móvel, através do qual as pessoas vão diariamente receber obras audiovisuais criadas com dados de sua região local, com relação às condições locais. O aplicativo irá gerar uma composição audiovisual, trabalhando com arte generativa, a partir da localização GPS do usuário, acessando dados de satélites e plataformas planetárias. A composição, que terá o formato de um curto vídeo de 20 a 30 segundos de duração, servirá como alerta para as condições climáticas locais e poderá ser compartilhada por meio das redes sociais (Instagram, FB, Twitter).

## Acesso e processamento dos dados do satélite

De minha parte, houve um enfoque maior no acesso à base de dados e tratamento dos mesmos, e tal é o assunto desse repositório. O contato com o Centro Pesquisas Meteorológicas e Climáticas Aplicadas a Agricultura (CEPAGRI) contribuiu para o acesso ao satélite meteorológico GOES-16 e seus produtos. Utilizando Python e algumas bibliotecas externas, foram criados códigos para a manipulação dos dados do satélite e assim possibilitar, posteriormente, a criação de composições audiovisuais exclusivas de cada acesso ao aplicativo, pois os dados do satélite mudam conforme hora e região. Dessa forma, esse é um dos passos para a construção do aplicativo previsto pelo projeto GaiaSenses.

## O que está contido no repositório?

Na pasta [docs](docs) estão os notebooks com a documentação dos códigos. Já na pasta [src](src), estão todos os códigos desenvolvidos no projeto, além de pastas com alguns exemplos de output e dos arquivos shapefile referentes ao Brasil. Cabe ressaltar que os códigos foram escritos e adaptados pensando no projeto GaiaSenses e nas necessidades que este teve até o momento, portanto tendem a ser específicos para os produtos escolhidos (chuvas, raios, ventos e incêndios). Mas, ao mesmo tempo, também são genéricos, então com algumas pequenas modificações podem atender outros produtos, isso é comentado melhor na documentação. Cabe ressaltar que há casos em que a parte de download está separada da parte de tratamento de dados, como no caso dos ventos (derived wind), porém em outros casos tudo está junto no mesmo código; isso foi apenas uma preferência para facilitar os trabalhos até então, mas que pode ser facilmente alterada, separando tais códigos em duas partes interligadas.

## Links que podem ser úteis:
- [Curso "Processamento de Dados de Satélites Geoestacionários com Python” fornecido pelo INPE (Instituto Nacional de Pesquisas Espaciais)](https://moodle.cptec.inpe.br/my/)
- [GOES-16/17 on Amazon Download Page](https://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_download.cgi?source=aws&satellite=noaa-goes16&domain=F&product=ABI-L2-RRQPE&date=2022-07-19&hour=16)
- [Programa de queimadas do INPE](https://queimadas.dgi.inpe.br/queimadas/dados-abertos/)
- [GOES-R Data Products (contém descrições e informações dos produtos do satélite GOES)](https://www.goes-r.gov/products/overview.html)