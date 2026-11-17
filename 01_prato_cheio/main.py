"""Prato Cheio - protótipo de console (ODS 2: Fome Zero e Agricultura Sustentável).

Uso:
    python main.py          -> menu interativo
    python main.py --demo   -> demonstração automática de todo o fluxo
"""
import sys
from datetime import datetime, timedelta

from prato_cheio import (ONG, AlimentoNaoPerecivel, AlimentoPerecivel, Plataforma,
                         Restaurante)


def carregar_exemplo(p):
    r1 = p.registrar_usuario(Restaurante("Cantina Sabor Capixaba", "contato@sabor.com", "Serra", "12.345.678/0001-90"))
    r2 = p.registrar_usuario(Restaurante("Padaria Pão Quente", "padaria@paoquente.com", "Serra", "98.765.432/0001-10"))
    o1 = p.registrar_usuario(ONG("Mãos que Alimentam", "ong@maos.org", "Serra", 60, 120))
    o2 = p.registrar_usuario(ONG("Cozinha Solidária ES", "cozinha@solidaria.org", "Serra", 20, 45))
    agora = datetime.now()
    p.publicar_doacao(r1.id, [
        AlimentoPerecivel("Arroz e feijão prontos", 15, agora + timedelta(hours=6)),
        AlimentoPerecivel("Frango assado", 8, agora + timedelta(hours=5)),
    ], horas_para_retirada=4)
    p.publicar_doacao(r2.id, [
        AlimentoPerecivel("Pães do dia", 10, agora + timedelta(hours=20), requer_refrigeracao=False),
        AlimentoNaoPerecivel("Biscoitos", 5, agora + timedelta(days=60), "caixa"),
    ], horas_para_retirada=8)
    return r1, r2, o1, o2


def demo():
    p = Plataforma()
    print("\n>>> 1) Cadastro de restaurantes, ONGs e doações")
    _, _, o1, o2 = carregar_exemplo(p)
    for u in p.listar_usuarios():
        print("  ", u)

    print("\n>>> 2) Doações disponíveis (ordenadas por urgência - polimorfismo)")
    for d in p.listar_disponiveis("Serra"):
        print("  ", d)

    print("\n>>> 3) ONGs reservam doações")
    primeira, segunda = p.listar_disponiveis("Serra")
    p.reservar(o1.id, primeira.id)
    print(f"   {o1.nome} reservou a doação #{primeira.id}")
    p.reservar(o2.id, segunda.id)
    print(f"   {o2.nome} reservou a doação #{segunda.id}")
    try:
        p.reservar(o1.id, primeira.id)   # tentativa de reservar de novo
    except ValueError as e:
        print("   Erro esperado (já reservada):", e)
    try:
        p.reservar(o2.id, primeira.id)   # passa da capacidade da ONG
    except ValueError as e:
        print("   Erro esperado (capacidade):", e)

    print("\n>>> 4) Retirada confirmada de uma doação")
    p.confirmar_retirada(primeira.id)
    print(f"   Doação #{primeira.id} retirada com sucesso.")

    print("\n>>> 5) Simulando 10 horas depois: a outra doação expira")
    p.atualizar_expiradas(datetime.now() + timedelta(hours=10))
    print("  ", p.buscar_doacao(segunda.id))

    print()
    print(p.gerar_relatorio().gerar_texto())


# ---------------------------- menu interativo ----------------------------
def ler_numero(msg, tipo=float):
    while True:
        try:
            return tipo(input(msg).replace(",", "."))
        except ValueError:
            print("  Valor inválido, tente de novo.")


def cadastrar_doacao(p):
    restaurantes = p.listar_usuarios(Restaurante)
    if not restaurantes:
        print("  Cadastre um restaurante primeiro.")
        return
    for r in restaurantes:
        print("  ", r)
    rid = ler_numero("ID do restaurante: ", int)
    itens = []
    while True:
        nome = input("  Nome do alimento (vazio para terminar): ").strip()
        if not nome:
            break
        kg = ler_numero("  Quantidade (kg): ")
        horas = ler_numero("  Validade do alimento (em horas): ")
        tipo = input("  Perecível? (s/n): ").strip().lower()
        validade = datetime.now() + timedelta(hours=horas)
        itens.append(AlimentoPerecivel(nome, kg, validade) if tipo == "s"
                     else AlimentoNaoPerecivel(nome, kg, validade))
    limite = ler_numero("Horas disponíveis para retirada: ")
    d = p.publicar_doacao(rid, itens, limite)
    print(f"  Doação #{d.id} cadastrada!")


def menu():
    p = Plataforma()
    opcoes = """
===== PRATO CHEIO =====
1 - Carregar dados de exemplo
2 - Cadastrar restaurante
3 - Cadastrar ONG
4 - Cadastrar doação (restaurante)
5 - Ver doações disponíveis
6 - Reservar doação (ONG)
7 - Confirmar retirada
8 - Relatório de impacto
0 - Sair"""
    while True:
        print(opcoes)
        op = input("Escolha: ").strip()
        try:
            if op == "1":
                carregar_exemplo(p)
                print("  Dados de exemplo carregados.")
            elif op == "2":
                r = p.registrar_usuario(Restaurante(input("  Nome: "), input("  E-mail: "),
                                                    input("  Cidade: "), input("  CNPJ: ")))
                print("  Cadastrado:", r)
            elif op == "3":
                o = p.registrar_usuario(ONG(input("  Nome: "), input("  E-mail: "), input("  Cidade: "),
                                            ler_numero("  Capacidade (kg): "),
                                            ler_numero("  Famílias atendidas: ", int)))
                print("  Cadastrada:", o)
            elif op == "4":
                cadastrar_doacao(p)
            elif op == "5":
                lista = p.listar_disponiveis()
                print("\n".join(f"  {d}" for d in lista) if lista else "  Nenhuma doação disponível.")
            elif op == "6":
                for o in p.listar_usuarios(ONG):
                    print("  ", o)
                p.reservar(ler_numero("ID da ONG: ", int), ler_numero("ID da doação: ", int))
                print("  Reserva realizada!")
            elif op == "7":
                p.confirmar_retirada(ler_numero("ID da doação: ", int))
                print("  Retirada confirmada!")
            elif op == "8":
                print(p.gerar_relatorio().gerar_texto())
            elif op == "0":
                print("Obrigado por ajudar a combater o desperdício!")
                break
            else:
                print("  Opção inválida.")
        except (ValueError, KeyError) as e:
            print("  Erro:", e)


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else menu()
