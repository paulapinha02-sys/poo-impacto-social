"""Gera o diagrama de classes UML do Prato Cheio (requer Graphviz: `dot`)."""
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

c = []
c.append(classe("Usuario",
    ["-id: int", "-nome: str", "-email: str", "-cidade: str"],
    ["+resumo(): str  {abstract}", "+__str__(): str"], abstrata=True, cor="#EAF2FB"))
c.append(classe("Restaurante",
    ["-cnpj: str", "-doacoes: list[Doacao]"],
    ["+cadastrar_doacao(itens, horas): Doacao", "+total_kg_doado(): float", "+resumo(): str"], cor="#EAF2FB"))
c.append(classe("ONG",
    ["-capacidade_kg: float", "-familias_atendidas: int", "-reservas: list[Reserva]"],
    ["+reservar(doacao): Reserva", "+kg_em_reserva(): float", "+total_kg_recebido(): float", "+resumo(): str"], cor="#EAF2FB"))
c.append(classe("Alimento",
    ["-nome: str", "-quantidade_kg: float", "-data_validade: datetime"],
    ["+horas_restantes(): float", "+esta_vencido(): bool", "+prioridade(): int  {abstract}", "+descricao(): str  {abstract}"],
    abstrata=True, cor="#FEF5E7"))
c.append(classe("AlimentoPerecivel",
    ["-requer_refrigeracao: bool"],
    ["+prioridade(): int", "+descricao(): str"], cor="#FEF5E7"))
c.append(classe("AlimentoNaoPerecivel",
    ["-embalagem: str"],
    ["+prioridade(): int", "+descricao(): str"], cor="#FEF5E7"))
c.append(classe("Doacao",
    ["-id: int", "-itens: list[Alimento]", "-criada_em: datetime", "-limite_retirada: datetime", "-status: StatusDoacao", "-reserva: Reserva"],
    ["+total_kg(): float", "+prioridade(): int", "+reservar(ong): Reserva", "+confirmar_retirada(): void", "+atualizar_status(): void"], cor="#EAF7EA"))
c.append(classe("Reserva",
    ["-data_reserva: datetime", "-data_retirada: datetime"],
    ["+confirmar(): void"], cor="#EAF7EA"))
c.append(classe("StatusDoacao",
    ["DISPONIVEL", "RESERVADA", "RETIRADA", "EXPIRADA"], [], estereotipo="enumeration", cor="#F4F4F4"))
c.append(classe("Plataforma",
    ["-nome: str", "-usuarios: dict", "-doacoes: dict"],
    ["+registrar_usuario(u): Usuario", "+publicar_doacao(id, itens, horas): Doacao", "+listar_disponiveis(): list[Doacao]",
     "+reservar(ong_id, doacao_id): Reserva", "+confirmar_retirada(doacao_id): void", "+gerar_relatorio(): RelatorioImpacto"], cor="#F3EAF9"))
c.append(classe("RelatorioImpacto",
    ["-kg_redistribuido: float", "-kg_perdido: float", "-ongs_atendidas: set", "-restaurantes_ativos: set"],
    ["+refeicoes_estimadas(): int", "+gerar_texto(): str"], cor="#F3EAF9"))

dot = """digraph G {
  graph [rankdir=BT, splines=ortho, nodesep=0.3, ranksep=0.45, dpi=170, bgcolor=white, pad=0.3,
         label=<<B>Diagrama de Classes UML - Solução 1: Prato Cheio (ODS 2)</B>>, labelloc=t, fontsize=20, fontname="Helvetica"];
  node [shape=plain, fontname="Helvetica", fontsize=11];
  edge [fontname="Helvetica", fontsize=10];
""" + "\n".join(c) + """
  {rank=same; Alimento; Reserva}
  // Herança (triângulo vazado)
  Restaurante -> Usuario [arrowhead=empty];
  ONG -> Usuario [arrowhead=empty];
  AlimentoPerecivel -> Alimento [arrowhead=empty];
  AlimentoNaoPerecivel -> Alimento [arrowhead=empty];

  // Composição: Doacao é composta por Alimentos (losango preenchido no lado da Doacao)
  Alimento -> Doacao [arrowhead=diamond, headlabel="1", taillabel="1..*", labeldistance=2.2, label=" composta de "];

  // Associações
  Doacao -> Restaurante [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.2, label=" cadastrada por "];
  Reserva -> Doacao [arrowhead=none, headlabel="1", taillabel="0..1", labeldistance=2.2, label=" referente a "];
  Reserva -> ONG [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.2, label=" feita por "];
  Doacao -> StatusDoacao [arrowhead=vee, style=dashed, label=" status "];

  // Agregação (losango vazado no lado da Plataforma)
  Usuario -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.2];
  Doacao -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.2];

  // Dependência
  Plataforma -> RelatorioImpacto [arrowhead=vee, style=dashed, label=" «cria» "];
}"""
open("diagrama_classes.dot", "w", encoding="utf-8").write(dot)
subprocess.run(["dot", "-Tpng", "diagrama_classes.dot", "-o", "diagrama_classes.png"], check=True)
subprocess.run(["dot", "-Tpdf", "diagrama_classes.dot", "-o", "diagrama_classes.pdf"], check=True)
print("ok")
