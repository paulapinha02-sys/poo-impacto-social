# 🌱 Tecnologia para o Impacto Social — POO

Três protótipos em **Python** (execução no terminal, sem bibliotecas externas) que usam **Programação Orientada a Objetos** para enfrentar problemas ligados aos **Objetivos de Desenvolvimento Sustentável (ODS)** da ONU.

| Projeto | ODS | O que faz | Pasta |
|---|---|---|---|
| 🍽️ **Prato Cheio** | 2 e 12 | Conecta restaurantes com excedente de comida a ONGs que combatem a fome. | [`01_prato_cheio`](01_prato_cheio) |
| 🎓 **Conecta Mentor** | 4 | Faz o match entre universitários voluntários e alunos da rede pública para reforço escolar. | [`02_conecta_mentor`](02_conecta_mentor) |
| ♻️ **EcoPonto** | 12 | Incentiva o descarte correto de lixo eletrônico com pontos e recompensas. | [`03_ecoponto`](03_ecoponto) |

## Como executar

Requisito: **Python 3.9 ou superior**. Entre na pasta de um projeto e rode:

```bash
cd 01_prato_cheio        # ou 02_conecta_mentor, 03_ecoponto
python main.py --demo    # demonstração automática de todo o fluxo
python main.py           # menu interativo
```

## Conceitos de POO presentes

Encapsulamento, herança, polimorfismo, abstração (classes abstratas), composição, agregação e associação, além do padrão **Strategy** no algoritmo de match do Conecta Mentor. Cada pasta tem um README com a tabela de onde cada conceito aparece e o **diagrama de classes UML** (`docs/diagrama_classes.png`).

## Uso de Inteligência Artificial

O código-base destes protótipos foi desenvolvido com o auxílio de uma ferramenta de IA (Claude, da Anthropic), conforme permitido no enunciado do trabalho. O autor revisou o código, executou os três protótipos e compreende a lógica de cada classe.

## Autor

Ana Paula da Cruz Pinha — 25210057
