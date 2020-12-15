# Projeto para FPRO
## FPRO/MIEIC, 2020/21
## André Ávila (up202006767)
## 1MIEIC04

### Objetivo

1. Criar um clone do jogo Archon - The Light and the Dark em Pygame.

2. Em alternativa... do clássico x em Pygame.

### Repositório de código

1) Link para o repositório do GitHub: https://github.com/AvilaAndre/projetofpro

2) Adicionar, como colaborador com permissão de leitura (*role read*), o Prof. da prática:

- https://github.com/AfonsoSalgadoSousa
- https://github.com/jlopes60
- https://github.com/nmacedo
- https://github.com/rpmcruz
- https://github.com/rcamacho

### Descrição

Archon é um jogo do género "battle chess", no caso do jogo Archon - The Light and The Dark o seu tabuleiro é de nove por nove, ao contrário dos habituais oito por oito do xadrez, tendo a variante de alguns dos seus quadrados mudarem de cor, isto deve-se ao facto do jogo dar vantagem à "peças" da luz quanto mais claro for o quadrado, esta mudança ocorre num ciclo.
A vantagem referida é usada quando duas peças (chamadas de "Icons") se disputam entre si, no xadrez a peça que captura fica no lugar e a outra sai de jogo, no Archon as duas peças batalham numa arena até à morte, prevalecendo no lugar a que vencer ou nenhuma no caso de ambas morrerem na batalha. Outra variante importante do jogo são os quadrados de poder que regeneram a vida da peça que lá esteja mais rápido, protegem a "peça" de feitiços inimigos e amigos e são um dos objetivos do jogo.
As peças do jogo são personagens, sendo que cada lado tem personagens únicas, cada tipo de personagem tem a sua habilidade e as suas próprias características como força, vida, velocidade, etc...
O jogo acaba quando todos os quadrados de poder estejam a ser ocupados por uma equipa ou quando alguma das equipas fica sem peças, caso as duas equipas fiquem sem peças o jogo termina num empate.
Este será um jogo multijogador local para duas pessoas.

### UI

![UI](https://github.com/fpro-feup/public/blob/master/recitas/ui.png)

A UI e as personagens vão ser desenhadas através do Aseprite [Aseprite](https://www.aseprite.org/) em pixel art e do pygame.draw (incluído no módulo Pygame).

### Pacotes

- Pygame

### Tarefas

1. Criar um menu principal, as regras e opções (para ver as teclas)
2. Criar um tabuleiro e as suas respetivas peças
3. Ser capaz de mover as peças, utilizar feitiços e começar uma luta.
4. Criar uma arena e seus obstáculos, criar movimentos e projéteis para os personagens e as suas mecânicas de combate.
5. Verificar o fim de jogo e poder voltar ao menu principal para repetir.

- Atualizado a última vez em 15/12/2020
