"""Gera o diagrama de classes UML do Conecta Mentor (requer Graphviz: `dot`)."""
import subprocess

def classe(nome, attrs, metodos, abstrata=False, estereotipo=None, cor="#FFFFFF"):
    def linhas(itens):
        return "".join(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT">{i}</TD></TR>' for i in itens) or '<TR><TD> </TD></TR>'
    titulo = f"<I>{nome}</I>" if abstrata else nome
    est = ""
    if abstrata:
        est = '<TR><TD><FONT POINT-SIZE="9">«abstract»</FONT></TD></TR>'
    if estereotipo:
        est = f'<TR><TD><FONT POINT-SIZE="9">«{estereotipo}»</FONT></TD></TR>'
    return (f'{nome} [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3" BGCOLOR="{cor}">'
            f'{est}<TR><TD><B>{titulo}</B></TD></TR>'
            f'<TR><TD><TABLE BORDER="0" CELLSPACING="0" CELLPADDING="1">{linhas(attrs)}</TABLE></TD></TR>'
            f'<TR><TD><TABLE BORDER="0" CELLSPACING="0" CELLPADDING="1">{linhas(metodos)}</TABLE></TD></TR>'
            f'</TABLE>>];')

AZ, LA, VE, RO, CI = "#EAF2FB", "#FEF5E7", "#EAF7EA", "#F3EAF9", "#F4F4F4"
c = [
 classe("Pessoa", ["-id: int", "-nome: str", "-email: str", "-cidade: str", "-disponibilidades: set[Horario]", "-sessoes: list[Sessao]"],
        ["+adicionar_disponibilidade(h): void", "+reservar_horario(h): void", "+liberar_horario(h): void", "+papel(): str  {abstract}", "+resumo(): str  {abstract}"], abstrata=True, cor=AZ),
 classe("Mentor", ["-curso: str", "-semestre: int", "-limite_sessoes: int", "-disciplinas: set[Disciplina]"],
        ["+adicionar_disciplina(d): void", "+ensina(d): bool", "+pode_aceitar(): bool", "+horas_voluntariado(): int", "+media_avaliacoes(): float", "+papel(): str", "+resumo(): str"], cor=AZ),
 classe("Mentorado", ["-escola: str", "-serie: str", "-dificuldades: set[Disciplina]"],
        ["+adicionar_dificuldade(d): void", "+papel(): str", "+resumo(): str"], cor=AZ),
 classe("Disciplina", ["-nome: str"], [], estereotipo="value object", cor=CI),
 classe("Horario", ["-dia: int", "-hora: int"], ["+de_texto(txt): Horario"], estereotipo="value object", cor=CI),
 classe("Sessao", ["-id: int", "-mentor: Mentor", "-mentorado: Mentorado", "-disciplina: Disciplina", "-horario: Horario", "-status: StatusSessao", "-avaliacao: Avaliacao"],
        ["+realizar(): void", "+cancelar(): void", "+avaliar(nota, comentario): void", "+como_participar(): str  {abstract}"], abstrata=True, cor=LA),
 classe("SessaoOnline", ["-link: str"], ["+como_participar(): str"], cor=LA),
 classe("SessaoPresencial", ["-local: str"], ["+como_participar(): str"], cor=LA),
 classe("Avaliacao", ["-nota: int", "-comentario: str"], [], estereotipo="value object", cor=CI),
 classe("StatusSessao", ["AGENDADA", "REALIZADA", "CANCELADA"], [], estereotipo="enumeration", cor=CI),
 classe("CriterioMatch", ["-peso: float"], ["+nome: str  {abstract}", "+pontuar(mentor, mentorado): float  {abstract}"], abstrata=True, cor=VE),
 classe("CriterioDisciplina", [], ["+pontuar(mentor, mentorado): float"], cor=VE),
 classe("CriterioHorario", [], ["+pontuar(mentor, mentorado): float"], cor=VE),
 classe("CriterioAvaliacao", [], ["+pontuar(mentor, mentorado): float"], cor=VE),
 classe("MotorDeMatch", ["-criterios: list[CriterioMatch]"], ["+sugerir(mentorado, mentores, limite): list[Sugestao]"], cor=VE),
 classe("Sugestao", ["-mentor: Mentor", "-pontuacao: float", "-disciplinas_comuns: tuple", "-horarios_comuns: tuple"], [], estereotipo="value object", cor=CI),
 classe("Plataforma", ["-nome: str", "-mentores: dict", "-mentorados: dict", "-sessoes: dict", "-motor: MotorDeMatch"],
        ["+registrar(pessoa): Pessoa", "+sugerir_mentores(id): list[Sugestao]", "+agendar(...): Sessao", "+realizar_sessao(id): void", "+cancelar_sessao(id): void", "+avaliar_sessao(id, nota): void", "+relatorio(): str"], cor=RO),
]

E = lambda *a: "  " + " ".join(a) + ";"
dot = """digraph G {
  graph [rankdir=BT, splines=polyline, nodesep=0.3, ranksep=0.45, dpi=150, bgcolor=white, pad=0.3,
         label=<<B>Diagrama de Classes UML - Solução 2: Conecta Mentor (ODS 4)</B>>, labelloc=t, fontsize=20, fontname="Helvetica"];
  node [shape=plain, fontname="Helvetica", fontsize=11];
  edge [fontname="Helvetica", fontsize=10];
""" + "\n".join(c) + """
  // Herança
  Mentor -> Pessoa [arrowhead=empty];
  Mentorado -> Pessoa [arrowhead=empty];
  SessaoOnline -> Sessao [arrowhead=empty];
  SessaoPresencial -> Sessao [arrowhead=empty];
  CriterioDisciplina -> CriterioMatch [arrowhead=empty];
  CriterioHorario -> CriterioMatch [arrowhead=empty];
  CriterioAvaliacao -> CriterioMatch [arrowhead=empty];

  // Composição (losango preenchido no lado do "todo")
  Horario -> Pessoa [arrowhead=diamond, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" disponibilidade "];
  Avaliacao -> Sessao [arrowhead=diamond, headlabel="1", taillabel="0..1", labeldistance=2.5];
  CriterioMatch -> MotorDeMatch [arrowhead=diamond, headlabel="1", taillabel="1..*", labeldistance=2.5];
  MotorDeMatch -> Plataforma [arrowhead=diamond, headlabel="1", taillabel="1", labeldistance=2.5];

  // Associações
  Sessao -> Mentor [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" conduzida por "];
  Sessao -> Mentorado [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" assistida por "];
  Sessao -> Disciplina [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" sobre "];
  Mentor -> Disciplina [arrowhead=none, headlabel="0..*", taillabel="0..*", labeldistance=2.5, label=" ensina "];
  Mentorado -> Disciplina [arrowhead=none, headlabel="0..*", taillabel="0..*", labeldistance=2.5, label=" dificuldade em "];
  Sessao -> StatusSessao [arrowhead=vee, style=dashed, label=" status "];

  // Agregação (losango vazado na Plataforma)
  Mentor -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
  Mentorado -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
  Sessao -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];

  // Dependência
  MotorDeMatch -> Sugestao [arrowhead=vee, style=dashed, label=" «cria» "];
}"""
open("diagrama_classes.dot", "w", encoding="utf-8").write(dot)
subprocess.run(["dot", "-Tpng", "diagrama_classes.dot", "-o", "diagrama_classes.png"], check=True)
subprocess.run(["dot", "-Tpdf", "diagrama_classes.dot", "-o", "diagrama_classes.pdf"], check=True)
print("ok")
