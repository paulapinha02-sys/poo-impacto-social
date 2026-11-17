# Solução 2 — Conecta Mentor (ODS 4)

## 1. Definição do problema e ODS

Muitos estudantes da rede pública chegam ao ensino fundamental e médio com lacunas de aprendizagem em disciplinas como Matemática e Português e não têm acesso a aulas particulares, que custam caro. Sem apoio, as lacunas se acumulam e aumentam a desigualdade de oportunidades. Do outro lado, há universitários dispostos a ajudar, mas sem um meio organizado de encontrar quem precisa, combinar horários e registrar a contribuição como horas de extensão.

**ODS relacionado:**
- **ODS 4 – Educação de Qualidade:** busca garantir educação inclusiva e equitativa e oportunidades de aprendizagem para todos. A plataforma oferece reforço escolar gratuito a quem não teria acesso.
- Dialoga também com o **ODS 10 – Redução das Desigualdades**, por aproximar estudantes de realidades diferentes.

## 2. Descrição do sistema (empreendedorismo social)

**Usuários:**
- **Mentores:** universitários voluntários. Informam curso, disciplinas que ensinam, horários livres e quantas sessões podem ter ao mesmo tempo.
- **Mentorados:** alunos da rede pública. Informam escola, série, disciplinas em que têm dificuldade e horários livres.

**Como funciona:** o sistema faz um **match** entre mentor e aluno. A pontuação combina três critérios com pesos: o quanto o mentor cobre as dificuldades do aluno (peso 5), quantos horários livres os dois têm em comum (peso 3) e a reputação do mentor pelas avaliações (peso 2). Mentores novos recebem nota neutra, para não serem prejudicados. Só são sugeridos mentores viáveis. O aluno agenda a sessão, que pode ser **online** (com link) ou **presencial** (por exemplo, na biblioteca da escola). Após a sessão, o aluno a avalia, e o mentor acumula **horas de voluntariado** que podem ser usadas como atividade de extensão. O relatório mostra alunos atendidos, horas entregues e disciplinas mais procuradas, ajudando escolas e a universidade a enxergar onde está a maior demanda.

**Sustentabilidade:**
- **Social:** reforço escolar gratuito reduz lacunas de aprendizagem e aproxima universidade e comunidade.
- **Econômica:** substitui aulas particulares pagas para famílias de baixa renda e dá ao universitário uma experiência prática e horas de extensão; a plataforma pode ser mantida por parcerias com universidades e secretarias de educação.
- **Ambiental:** o formato online evita deslocamentos e reduz o uso de materiais impressos.

## 3. Modelagem orientada a objetos

O diagrama (`diagrama_classes.png`) tem **17 classes/tipos**, entre elas `Pessoa`, `Mentor`, `Mentorado`, `Disciplina`, `Horario`, `Sessao`, `SessaoOnline`, `SessaoPresencial`, `Avaliacao`, `StatusSessao`, `CriterioMatch` (com três subclasses), `MotorDeMatch`, `Sugestao` e `Plataforma`.

- **Herança:** `Mentor` e `Mentorado` herdam de `Pessoa` (dados e agenda comuns); `SessaoOnline` e `SessaoPresencial` herdam de `Sessao`; `CriterioDisciplina`, `CriterioHorario` e `CriterioAvaliacao` herdam de `CriterioMatch`.
- **Polimorfismo:** o método `como_participar()` retorna um link na sessão online e um endereço na presencial; o método `pontuar()` calcula a nota de compatibilidade de forma diferente em cada critério, e o `MotorDeMatch` os usa sem saber qual é qual (padrão Strategy). O mesmo vale para `resumo()` em `Pessoa`.
- **Encapsulamento:** atributos privados com `@property`; `Disciplina`, `Horario` e `Avaliacao` são imutáveis e se validam sozinhos (nota de 1 a 5, hora entre 6 e 21). As regras de negócio (horário livre, limite de sessões, só avaliar sessões realizadas) ficam dentro das classes, não espalhadas pelo programa.
- **Composição:** `Pessoa` possui seus `Horario`s, `Sessao` possui sua `Avaliacao` e `Plataforma` possui o `MotorDeMatch`.
- **Agregação:** `Plataforma` agrega mentores, mentorados e sessões.
- **Associação:** `Sessao` liga um mentor, um mentorado, uma disciplina e um horário; mentores e mentorados se associam a `Disciplina`.
- **Dependência:** `MotorDeMatch` cria objetos `Sugestao`.

## 4. Protótipo

Código em Python com menu de console e modo de demonstração (`python main.py --demo`). Repositório: *<link do GitHub>*.
