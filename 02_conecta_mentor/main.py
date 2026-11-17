"""Conecta Mentor - protótipo de console (ODS 4: Educação de Qualidade).

Uso:
    python main.py          -> menu interativo
    python main.py --demo   -> demonstração automática de todo o fluxo
"""
import sys

from conecta_mentor import Disciplina, Horario, Mentor, Mentorado, Plataforma


def _novo_mentor(nome, curso, sem, disciplinas, horarios, limite=3):
    m = Mentor(nome, f"{nome.split()[0].lower()}@universidade.edu", "Serra", curso, sem, limite)
    for d in disciplinas:
        m.adicionar_disciplina(Disciplina(d))
    for h in horarios:
        m.adicionar_disponibilidade(Horario.de_texto(h))
    return m


def _novo_mentorado(nome, escola, serie, dificuldades, horarios):
    a = Mentorado(nome, f"{nome.split()[0].lower()}@email.com", "Serra", escola, serie)
    for d in dificuldades:
        a.adicionar_dificuldade(Disciplina(d))
    for h in horarios:
        a.adicionar_disponibilidade(Horario.de_texto(h))
    return a


def carregar_exemplo(p):
    ana = p.registrar(_novo_mentor("Ana Souza", "Engenharia", 6, ["Matemática", "Física"], ["ter 14", "qua 15", "sex 10"]))
    bruno = p.registrar(_novo_mentor("Bruno Lima", "Letras", 5, ["Português", "Redação", "História"], ["seg 14", "qua 15"]))
    carla = p.registrar(_novo_mentor("Carla Reis", "Química", 7, ["Matemática", "Química"], ["ter 14", "qui 16"], limite=1))
    davi = p.registrar(_novo_mentorado("Davi Alves", "EMEF Jardim Limoeiro", "9º ano", ["Matemática", "Física"], ["ter 14", "sex 10", "qua 15"]))
    edu = p.registrar(_novo_mentorado("Eduarda Melo", "EEEFM Maria Ortiz", "2º ano EM", ["Português", "Redação"], ["seg 14", "qua 15", "qui 16"]))
    fel = p.registrar(_novo_mentorado("Felipe Costa", "EMEF Novo Horizonte", "8º ano", ["Matemática", "Química"], ["qui 16", "ter 14"]))
    return ana, bruno, carla, davi, edu, fel


def mostrar_sugestoes(p, mentorado):
    print(f"  Sugestões para {mentorado.nome} (dificuldades: "
          f"{', '.join(sorted(d.nome for d in mentorado.dificuldades))}):")
    sugestoes = p.sugerir_mentores(mentorado.id)
    if not sugestoes:
        print("    Nenhum mentor compatível no momento.")
    for s in sugestoes:
        print(f"    {s.pontuacao * 100:5.1f}%  {s.mentor.nome} - cobre {', '.join(s.disciplinas_comuns)} "
              f"| horários em comum: {', '.join(str(h) for h in s.horarios_comuns)}")
    return sugestoes


def demo():
    p = Plataforma()
    print("\n>>> 1) Cadastro de mentores e mentorados")
    ana, bruno, carla, davi, edu, fel = carregar_exemplo(p)
    for pessoa in p.listar_mentores() + p.listar_mentorados():
        print("  ", pessoa)          # polimorfismo: cada subclasse tem o seu resumo()

    print("\n>>> 2) Match: critérios com pesos ->",
          ", ".join(f"{c.nome} (peso {c.peso})" for c in p.motor.criterios))
    mostrar_sugestoes(p, davi)
    mostrar_sugestoes(p, edu)
    mostrar_sugestoes(p, fel)

    print("\n>>> 3) Agendamento (modalidades diferentes, mesmo método como_participar)")
    s1 = p.agendar(ana.id, davi.id, "Matemática", Horario.de_texto("ter 14"))
    s2 = p.agendar(bruno.id, edu.id, "Redação", Horario.de_texto("qua 15"),
                   modalidade="presencial", detalhe="Biblioteca da EEEFM Maria Ortiz")
    s3 = p.agendar(carla.id, fel.id, "Química", Horario.de_texto("qui 16"))
    for s in (s1, s2, s3):
        print("  ", s)

    print("\n>>> 4) Regras de negócio protegendo o sistema")
    for descricao, tentativa in [
        ("Horário já ocupado", lambda: p.agendar(ana.id, davi.id, "Física", Horario.de_texto("ter 14"))),
        ("Mentor não ensina a matéria", lambda: p.agendar(ana.id, davi.id, "Redação", Horario.de_texto("sex 10"))),
        ("Mentor no limite de sessões", lambda: p.agendar(carla.id, davi.id, "Matemática", Horario.de_texto("ter 14"))),
    ]:
        try:
            tentativa()
        except ValueError as e:
            print(f"   {descricao}: {e}")

    print("\n>>> 5) Cancelamento libera o horário para novos matches")
    p.cancelar_sessao(s3.id)
    print(f"   Sessão #{s3.id} cancelada. Sugestões de Felipe agora:")
    mostrar_sugestoes(p, fel)

    print("\n>>> 6) Sessões realizadas e avaliadas")
    p.realizar_sessao(s1.id)
    p.avaliar_sessao(s1.id, 5, "Explicou equações do 1º grau com muita paciência!")
    p.realizar_sessao(s2.id)
    p.avaliar_sessao(s2.id, 4)
    print("   Sessões #1 e #2 realizadas e avaliadas.")
    try:
        p.avaliar_sessao(s3.id, 5)
    except ValueError as e:
        print("   Erro esperado:", e)

    print()
    print(p.relatorio())


# ---------------------------- menu interativo ----------------------------
def ler_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  Digite um número inteiro.")


def ler_lista(msg):
    return [x.strip() for x in input(msg).split(",") if x.strip()]


def menu():
    p = Plataforma()
    opcoes = """
===== CONECTA MENTOR =====
1 - Carregar dados de exemplo
2 - Cadastrar mentor
3 - Cadastrar mentorado
4 - Ver pessoas cadastradas
5 - Sugerir mentores para um mentorado
6 - Agendar sessão
7 - Ver sessões
8 - Realizar sessão
9 - Cancelar sessão
10 - Avaliar sessão
11 - Relatório de impacto
0 - Sair"""
    while True:
        print(opcoes)
        op = input("Escolha: ").strip()
        try:
            if op == "1":
                carregar_exemplo(p)
                print("  Dados de exemplo carregados.")
            elif op == "2":
                m = Mentor(input("  Nome: "), input("  E-mail: "), input("  Cidade: "),
                           input("  Curso: "), ler_int("  Semestre: "), ler_int("  Máx. de sessões simultâneas: "))
                for d in ler_lista("  Disciplinas que ensina (separe por vírgula): "):
                    m.adicionar_disciplina(Disciplina(d))
                for h in ler_lista("  Horários livres (ex.: ter 14, qua 15): "):
                    m.adicionar_disponibilidade(Horario.de_texto(h))
                print("  Cadastrado:", p.registrar(m))
            elif op == "3":
                a = Mentorado(input("  Nome: "), input("  E-mail: "), input("  Cidade: "),
                              input("  Escola: "), input("  Série: "))
                for d in ler_lista("  Disciplinas com dificuldade (separe por vírgula): "):
                    a.adicionar_dificuldade(Disciplina(d))
                for h in ler_lista("  Horários livres (ex.: ter 14, qua 15): "):
                    a.adicionar_disponibilidade(Horario.de_texto(h))
                print("  Cadastrado:", p.registrar(a))
            elif op == "4":
                for pessoa in p.listar_mentores() + p.listar_mentorados():
                    print("  ", pessoa)
            elif op == "5":
                mostrar_sugestoes(p, p.buscar_mentorado(ler_int("  ID do mentorado: ")))
            elif op == "6":
                mid, aid = ler_int("  ID do mentor: "), ler_int("  ID do mentorado: ")
                disc = input("  Disciplina: ")
                h = Horario.de_texto(input("  Horário (ex.: ter 14): "))
                mod = input("  Modalidade (online/presencial): ").strip().lower() or "online"
                det = input("  Link (online, opcional) ou local (presencial): ").strip() or None
                print("  Agendada!\n  ", p.agendar(mid, aid, disc, h, mod, det))
            elif op == "7":
                sessoes = p.listar_sessoes()
                print("\n".join(f"  {s}" for s in sessoes) if sessoes else "  Nenhuma sessão.")
            elif op == "8":
                p.realizar_sessao(ler_int("  ID da sessão: "))
                print("  Sessão marcada como realizada.")
            elif op == "9":
                p.cancelar_sessao(ler_int("  ID da sessão: "))
                print("  Sessão cancelada; horários liberados.")
            elif op == "10":
                p.avaliar_sessao(ler_int("  ID da sessão: "), ler_int("  Nota (1 a 5): "), input("  Comentário: "))
                print("  Avaliação registrada.")
            elif op == "11":
                print(p.relatorio())
            elif op == "0":
                print("Obrigado por levar educação a quem precisa!")
                break
            else:
                print("  Opção inválida.")
        except ValueError as e:
            print("  Erro:", e)


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else menu()
