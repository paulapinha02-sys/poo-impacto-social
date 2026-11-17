"""Gera o diagrama de classes UML do EcoPonto (requer Graphviz: `dot`)."""
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
 classe("Usuario", ["-id: int", "-nome: str", "-email: str", "-cidade: str"], ["+resumo(): str  {abstract}"], abstrata=True, cor=AZ),
 classe("Cidadao", ["-saldo: int", "-acumulados: int", "-entregas: list[Entrega]", "-resgates: list[Resgate]"],
        ["+creditar(pontos): void", "+debitar(pontos): void", "+nivel(): str", "+multiplicador(): float", "+total_kg_entregue(): float", "+resumo(): str"], cor=AZ),
 classe("Parceiro", ["-ramo: str", "-recompensas: list[Recompensa]"], ["+cadastrar_recompensa(nome, custo, estoque): Recompensa", "+resumo(): str"], cor=AZ),
 classe("ItemEletronico", ["-descricao: str", "-peso_kg: float"],
        ["+categoria(): str  {abstract}", "+calcular_pontos(): int  {abstract}", "+destino(): DestinoFinal  {abstract}"], abstrata=True, cor=LA),
 classe("Celular", ["-funcional: bool"], ["+categoria(): str", "+calcular_pontos(): int", "+destino(): DestinoFinal"], cor=LA),
 classe("Bateria", ["-tipo: str"], ["+categoria(): str", "+calcular_pontos(): int", "+destino(): DestinoFinal"], cor=LA),
 classe("Computador", ["-notebook: bool"], ["+categoria(): str", "+calcular_pontos(): int", "+destino(): DestinoFinal"], cor=LA),
 classe("Eletrodomestico", [], ["+categoria(): str", "+calcular_pontos(): int", "+destino(): DestinoFinal"], cor=LA),
 classe("DestinoFinal", ["RECONDICIONAMENTO", "RECICLAGEM", "RESIDUO_PERIGOSO"], [], estereotipo="enumeration", cor=CI),
 classe("PontoDeColeta", ["-id: int", "-nome: str", "-endereco: str", "-capacidade_kg: float", "-categorias: frozenset", "-estoque_kg: float"],
        ["+validar_recebimento(itens): void", "+receber(itens): void", "+coletar(): float"], cor=VE),
 classe("Entrega", ["-cidadao: Cidadao", "-ponto: PontoDeColeta", "-itens: list[ItemEletronico]", "-data: datetime", "-pontos_base: int", "-bonus: int"],
        ["+pontos_total(): int", "+peso_total(): float"], cor=VE),
 classe("Recompensa", ["-id: int", "-nome: str", "-custo_pontos: int", "-estoque: int"], ["+retirar_do_estoque(): void"], cor=VE),
 classe("Resgate", ["-cidadao: Cidadao", "-recompensa: Recompensa", "-data: datetime"], [], cor=VE),
 classe("Plataforma", ["-nome: str", "-usuarios: dict", "-pontos: dict", "-entregas: list", "-resgates: list"],
        ["+registrar_usuario(u): Usuario", "+registrar_ponto(p): PontoDeColeta", "+entregar(cidadao_id, ponto_id, itens): Entrega", "+resgatar(cidadao_id, recompensa_id): Resgate", "+coletar_ponto(ponto_id): float", "+relatorio(): str"], cor=RO),
]
dot = """digraph G {
  graph [rankdir=BT, splines=polyline, nodesep=0.3, ranksep=0.45, dpi=150, bgcolor=white, pad=0.3,
         label=<<B>Diagrama de Classes UML - Solução 3: EcoPonto (ODS 12)</B>>, labelloc=t, fontsize=20, fontname="Helvetica"];
  node [shape=plain, fontname="Helvetica", fontsize=11];
  edge [fontname="Helvetica", fontsize=10];
""" + "\n".join(c) + """
  // Herança
  Cidadao -> Usuario [arrowhead=empty];
  Parceiro -> Usuario [arrowhead=empty];
  Celular -> ItemEletronico [arrowhead=empty];
  Bateria -> ItemEletronico [arrowhead=empty];
  Computador -> ItemEletronico [arrowhead=empty];
  Eletrodomestico -> ItemEletronico [arrowhead=empty];

  // Composição
  ItemEletronico -> Entrega [arrowhead=diamond, headlabel="1", taillabel="1..*", labeldistance=2.5, label=" composta de "];
  Recompensa -> Parceiro [arrowhead=diamond, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" oferece "];

  // Associações
  Entrega -> Cidadao [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" feita por "];
  Entrega -> PontoDeColeta [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" recebida em "];
  Resgate -> Cidadao [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" feito por "];
  Resgate -> Recompensa [arrowhead=none, headlabel="1", taillabel="0..*", labeldistance=2.5, label=" troca por "];
  ItemEletronico -> DestinoFinal [arrowhead=vee, style=dashed, label=" destino "];

  // Agregação
  Usuario -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
  PontoDeColeta -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
  Entrega -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
  Resgate -> Plataforma [arrowhead=odiamond, headlabel="1", taillabel="0..*", labeldistance=2.5];
}"""
open("diagrama_classes.dot", "w", encoding="utf-8").write(dot)
subprocess.run(["dot", "-Tpng", "diagrama_classes.dot", "-o", "diagrama_classes.png"], check=True)
subprocess.run(["dot", "-Tpdf", "diagrama_classes.dot", "-o", "diagrama_classes.pdf"], check=True)
print("ok")
