# Solução 3 — EcoPonto (ODS 12)

## 1. Definição do problema e ODS

Celulares, baterias, computadores e eletrodomésticos antigos costumam ficar esquecidos em gavetas ou acabam no lixo comum. Esses aparelhos contêm metais e substâncias tóxicas, como as presentes em pilhas e baterias, que contaminam solo e água quando descartados de forma errada, além de desperdiçar materiais que poderiam ser reaproveitados. Muita gente não sabe onde descartar corretamente e não tem nenhum incentivo para fazer o esforço.

**ODS relacionado:**
- **ODS 12 – Consumo e Produção Responsáveis:** as metas 12.4 (gestão ambientalmente adequada de resíduos) e 12.5 (redução da geração de resíduos por reciclagem e reúso) são o foco da plataforma, que incentiva o descarte correto e o reaproveitamento.

## 2. Descrição do sistema (empreendedorismo social)

**Usuários:**
- **Cidadãos:** entregam eletrônicos nos pontos de coleta, acumulam pontos e trocam por recompensas.
- **Parceiros:** comércios locais (mercado, cafeteria etc.) que oferecem recompensas em troca de pontos, ganhando visibilidade e clientes.
- **Pontos de coleta:** locais físicos (escolas, mercados, prefeitura) com capacidade e categorias aceitas. Uma cooperativa de reciclagem retira o material periodicamente.

**Como funciona:** o cidadão leva os itens a um ponto de coleta. Cada tipo de item vale uma quantidade diferente de pontos: um celular que ainda funciona vale mais, pois pode ser recondicionado e doado; pilhas e baterias valem proporcionalmente mais por serem resíduo perigoso; computadores e eletrodomésticos são calculados pelo peso. O sistema também define o **destino final** de cada item (reúso, reciclagem ou descarte especial). O cidadão sobe de nível (Bronze, Prata, Ouro) conforme acumula pontos, ganhando um bônus nas próximas entregas, e troca os pontos por recompensas. O relatório ambiental mostra quanto material foi descartado corretamente, por categoria e por destino, além de um ranking de cidadãos.

**Sustentabilidade:**
- **Ambiental:** evita contaminação por metais pesados, promove reúso e reciclagem e reduz a extração de novos recursos.
- **Social:** cria o hábito do descarte correto, gera renda para cooperativas de catadores e permite a doação de aparelhos recondicionados.
- **Econômica:** comércios parceiros atraem clientes; a plataforma pode ser sustentada por parcerias com prefeituras, empresas (que têm obrigação de logística reversa) e recicladoras.

## 3. Modelagem orientada a objetos

O diagrama (`diagrama_classes.png`) tem **14 classes/tipos**: `Usuario`, `Cidadao`, `Parceiro`, `ItemEletronico`, `Celular`, `Bateria`, `Computador`, `Eletrodomestico`, `DestinoFinal` (enumeração), `PontoDeColeta`, `Entrega`, `Recompensa`, `Resgate` e `Plataforma`.

- **Herança:** `Cidadao` e `Parceiro` herdam de `Usuario`; `Celular`, `Bateria`, `Computador` e `Eletrodomestico` herdam de `ItemEletronico`.
- **Polimorfismo:** `calcular_pontos()`, `destino()` e `categoria()` são abstratos em `ItemEletronico` e cada subclasse os implementa com sua regra (por exemplo, o celular depende de estar funcionando; a bateria, do peso). A `Entrega` soma os pontos de uma lista de itens sem precisar saber o tipo de cada um, e o relatório agrupa por destino da mesma forma.
- **Encapsulamento:** atributos privados com `@property`. O saldo só muda por `creditar()` e `debitar()` (que impede saldo negativo); o estoque de uma recompensa só muda por `retirar_do_estoque()`; o ponto de coleta valida categoria aceita e capacidade antes de receber, e a `Entrega` valida antes de alterar qualquer estado.
- **Composição:** `Entrega` é composta de `ItemEletronico`s; `Parceiro` possui suas `Recompensa`s.
- **Agregação:** `Plataforma` agrega usuários, pontos de coleta, entregas e resgates.
- **Associação:** `Entrega` liga um `Cidadao` a um `PontoDeColeta`; `Resgate` liga um `Cidadao` a uma `Recompensa`.

## 4. Protótipo

Código em Python com menu de console e modo de demonstração (`python main.py --demo`). Repositório: *<link do GitHub>*.
