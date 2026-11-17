# Solução 1 — Prato Cheio (ODS 2 e ODS 12)

## 1. Definição do problema e ODS

Todos os dias, restaurantes, padarias e cantinas descartam alimentos que ainda estão próprios para o consumo, porque o excedente não tem para onde ir antes de estragar. Ao mesmo tempo, muitas famílias enfrentam insegurança alimentar e as ONGs que as atendem dependem de doações irregulares, sem saber o que, quanto e quando vão receber. O problema, portanto, não é só a falta de comida, mas a **falta de conexão eficiente entre quem tem sobra e quem tem necessidade**.

**ODS relacionados:**
- **ODS 2 – Fome Zero e Agricultura Sustentável:** direciona alimento a quem precisa, contribuindo para acabar com a fome e melhorar a segurança alimentar.
- **ODS 12 – Consumo e Produção Responsáveis:** a meta 12.3 trata de reduzir o desperdício de alimentos; a plataforma evita que o excedente vire lixo.

## 2. Descrição do sistema (empreendedorismo social)

**Usuários:**
- **Restaurantes/padarias** (doadores): cadastram o excedente do dia, informando tipo de alimento, quantidade, validade e prazo para retirada.
- **ONGs** (receptoras): consultam as doações disponíveis na sua cidade e reservam o que conseguem retirar e armazenar.

**Como funciona na prática:** o restaurante registra a doação; o sistema classifica cada alimento por urgência (um prato pronto que vence em poucas horas é mais urgente que um pacote de biscoitos) e mostra primeiro o que está mais perto de estragar. A ONG reserva, retira dentro do prazo e confirma. Se ninguém retirar a tempo, a doação expira e é contabilizada como perda, para a plataforma poder melhorar. Ao final, o sistema gera um **relatório de impacto** com quilos redistribuídos, refeições estimadas e taxa de aproveitamento.

**Sustentabilidade:**
- **Social:** mais alimento chega a famílias em vulnerabilidade, com transparência sobre o destino da doação.
- **Econômica:** restaurantes reduzem custos de descarte e podem usar o relatório como comprovação de responsabilidade social; ONGs planejam melhor seu estoque.
- **Ambiental:** menos alimento no lixo significa menos resíduos orgânicos em aterros e menos emissão de gases de efeito estufa.

## 3. Modelagem orientada a objetos

O diagrama de classes (`diagrama_classes.png`) tem **11 classes/tipos**: `Usuario`, `Restaurante`, `ONG`, `Alimento`, `AlimentoPerecivel`, `AlimentoNaoPerecivel`, `Doacao`, `Reserva`, `StatusDoacao` (enumeração), `Plataforma` e `RelatorioImpacto`.

- **Herança:** `Restaurante` e `ONG` herdam de `Usuario` (dados comuns como nome, e-mail e cidade); `AlimentoPerecivel` e `AlimentoNaoPerecivel` herdam de `Alimento`.
- **Polimorfismo:** o método `prioridade()` de `Alimento` é implementado de forma diferente em cada subclasse (perecível é urgente quando restam 12 horas ou menos; não perecível só ganha atenção na última semana). Assim, a `Plataforma` ordena as doações por urgência sem precisar saber o tipo de cada item. O mesmo vale para `resumo()` em `Usuario` e `descricao()` em `Alimento`.
- **Encapsulamento:** todos os atributos são privados (prefixo `_`) e acessados por `@property`. A lista de itens de uma `Doacao` é devolvida como tupla, impedindo alteração externa. O status só muda por métodos que validam a transição (`reservar`, `confirmar_retirada`).
- **Composição:** uma `Doacao` é composta por `Alimento`s, que só existem dentro dela.
- **Agregação:** a `Plataforma` agrega `Usuario`s e `Doacao`ões, que existem independentemente dela.
- **Associação:** `Restaurante` cadastra `Doacao`; `Reserva` liga uma `Doacao` a uma `ONG`.
- **Dependência:** `Plataforma` cria o `RelatorioImpacto`.

## 4. Protótipo

Código em Python com menu de console e modo de demonstração (`python main.py --demo`). Repositório: *<link do GitHub>*.
