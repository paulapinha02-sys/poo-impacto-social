"""EcoPonto - protótipo de console (ODS 12: Consumo e Produção Responsáveis).

Uso:
    python main.py          -> menu interativo
    python main.py --demo   -> demonstração automática de todo o fluxo
"""
import sys

from ecoponto import (Bateria, Celular, Cidadao, Computador, Eletrodomestico, Parceiro,
                      Plataforma, PontoDeColeta)

TODAS = ["Celular", "Bateria", "Computador", "Eletrodoméstico"]


def carregar_exemplo(p):
    ana = p.registrar_usuario(Cidadao("Ana Souza", "ana@email.com", "Serra"))
    bruno = p.registrar_usuario(Cidadao("Bruno Lima", "bruno@email.com", "Serra"))
    mercado = p.registrar_usuario(Parceiro("Mercado Bom Preço", "contato@bompreco.com", "Serra", "Supermercado"))
    cafe = p.registrar_usuario(Parceiro("Café Central", "cafe@central.com", "Serra", "Cafeteria"))
    mercado.cadastrar_recompensa("Desconto de R$ 10 em compras", 150, 5)
    mercado.cadastrar_recompensa("Cesta básica", 600, 2)
    cafe.cadastrar_recompensa("Café + pão de queijo", 60, 10)
    centro = p.registrar_ponto(PontoDeColeta("EcoPonto Centro", "Av. Principal, 100", "Serra", 30, TODAS))
    escola = p.registrar_ponto(PontoDeColeta("EcoPonto Escola", "Rua das Flores, 20", "Serra", 5, ["Celular", "Bateria"]))
    return ana, bruno, centro, escola


def demo():
    p = Plataforma()
    print("\n>>> 1) Cadastros (cidadãos, parceiros, pontos de coleta, recompensas)")
    ana, bruno, centro, escola = carregar_exemplo(p)
    for u in p.listar_usuarios():
        print("  ", u)
    for pt in p.listar_pontos():
        print("  ", pt)
    for r in p.listar_recompensas():
        print("  ", r)

    print("\n>>> 2) Polimorfismo: cada item calcula seus pontos e seu destino de um jeito")
    itens = [Celular("Celular Samsung A10 funcionando", 0.18, funcional=True),
             Celular("Celular antigo quebrado", 0.15),
             Bateria("Bateria de notebook", 0.35),
             Computador("Notebook Dell antigo", 2.4),
             Eletrodomestico("Liquidificador", 1.8)]
    for i in itens:
        print("  ", i)

    print("\n>>> 3) Entregas e bônus por nível (Bronze 1.0x, Prata 1.1x, Ouro 1.2x)")
    for lote in (itens[:3], [itens[3]], [itens[4]]):
        e = p.entregar(ana.id, centro.id, lote)
        print("  ", e)
        print(f"      Saldo de {ana.nome}: {ana.saldo} pts | nível: {ana.nivel()}")

    print("\n>>> 4) Regras de negócio protegendo o sistema")
    tentativas = [
        ("Ponto não aceita a categoria", lambda: p.entregar(bruno.id, escola.id, [Computador("PC de mesa", 7)])),
        ("Ponto sem capacidade", lambda: p.entregar(bruno.id, escola.id, [Bateria("Lote de baterias", 5.5)])),
        ("Saldo insuficiente", lambda: p.resgatar(bruno.id, 2)),
    ]
    for desc, fn in tentativas:
        try:
            fn()
        except ValueError as e:
            print(f"   {desc}: {e}")

    print("\n>>> 5) Resgate de recompensas")
    p.entregar(bruno.id, escola.id, [Celular("Celular com tela trincada", 0.2, funcional=True), Bateria("Pilhas AA usadas", 0.4)])
    r = p.resgatar(ana.id, 3)
    print(f"   {ana.nome} resgatou '{r.recompensa.nome}' | saldo: {ana.saldo} pts")
    r = p.resgatar(bruno.id, 3)
    print(f"   {bruno.nome} resgatou '{r.recompensa.nome}' | saldo: {bruno.saldo} pts")

    print("\n>>> 6) Cooperativa retira o material do ponto")
    kg = p.coletar_ponto(centro.id)
    print(f"   {kg:.2f} kg encaminhados para reciclagem. Estoque do ponto agora: {centro.estoque_kg:.2f} kg")

    print()
    print(p.relatorio())


# ---------------------------- menu interativo ----------------------------
def ler_num(msg, tipo=float):
    while True:
        try:
            return tipo(input(msg).replace(",", "."))
        except ValueError:
            print("  Valor inválido, tente de novo.")


def montar_itens():
    itens = []
    tipos = {"1": "Celular", "2": "Bateria", "3": "Computador", "4": "Eletrodoméstico"}
    while True:
        op = input("  Tipo do item (1-Celular 2-Bateria 3-Computador 4-Eletrodoméstico, vazio p/ terminar): ").strip()
        if not op:
            return itens
        if op not in tipos:
            print("  Opção inválida.")
            continue
        desc = input("  Descrição: ")
        peso = ler_num("  Peso (kg): ")
        if op == "1":
            itens.append(Celular(desc, peso, input("  Está funcionando? (s/n): ").strip().lower() == "s"))
        elif op == "2":
            itens.append(Bateria(desc, peso))
        elif op == "3":
            itens.append(Computador(desc, peso))
        else:
            itens.append(Eletrodomestico(desc, peso))


def menu():
    p = Plataforma()
    opcoes = """
===== ECOPONTO =====
1 - Carregar dados de exemplo
2 - Cadastrar cidadão
3 - Cadastrar parceiro (e recompensa)
4 - Cadastrar ponto de coleta
5 - Ver cadastros
6 - Registrar entrega de eletrônicos
7 - Resgatar recompensa
8 - Coletar material de um ponto
9 - Relatório ambiental
0 - Sair"""
    while True:
        print(opcoes)
        op = input("Escolha: ").strip()
        try:
            if op == "1":
                carregar_exemplo(p)
                print("  Dados de exemplo carregados.")
            elif op == "2":
                print("  Cadastrado:", p.registrar_usuario(Cidadao(input("  Nome: "), input("  E-mail: "), input("  Cidade: "))))
            elif op == "3":
                parc = p.registrar_usuario(Parceiro(input("  Nome: "), input("  E-mail: "), input("  Cidade: "), input("  Ramo: ")))
                parc.cadastrar_recompensa(input("  Nome da recompensa: "), ler_num("  Custo em pontos: ", int), ler_num("  Estoque: ", int))
                print("  Cadastrado:", parc)
            elif op == "4":
                cats = input("  Categorias aceitas (separe por vírgula, ex.: Celular, Bateria): ")
                pt = p.registrar_ponto(PontoDeColeta(input("  Nome: "), input("  Endereço: "), input("  Cidade: "),
                                                     ler_num("  Capacidade (kg): "),
                                                     [c.strip() for c in cats.split(",") if c.strip()]))
                print("  Cadastrado:", pt)
            elif op == "5":
                for x in p.listar_usuarios() + p.listar_pontos() + p.listar_recompensas():
                    print("  ", x)
            elif op == "6":
                cid, pid = ler_num("  ID do cidadão: ", int), ler_num("  ID do ponto: ", int)
                print("  ", p.entregar(cid, pid, montar_itens()))
            elif op == "7":
                r = p.resgatar(ler_num("  ID do cidadão: ", int), ler_num("  ID da recompensa: ", int))
                print(f"  Resgatado: {r.recompensa.nome}. Saldo restante: {r.cidadao.saldo} pts")
            elif op == "8":
                print(f"  {p.coletar_ponto(ler_num('  ID do ponto: ', int)):.2f} kg coletados.")
            elif op == "9":
                print(p.relatorio())
            elif op == "0":
                print("Obrigado por descartar do jeito certo!")
                break
            else:
                print("  Opção inválida.")
        except ValueError as e:
            print("  Erro:", e)


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else menu()
