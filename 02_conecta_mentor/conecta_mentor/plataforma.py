"""Plataforma: ponto central que cadastra pessoas, sugere matches e gerencia sessões."""
from collections import Counter

from .match import MotorDeMatch
from .modelos import (Disciplina, Mentor, Mentorado, SessaoOnline, SessaoPresencial,
                      StatusSessao)


class Plataforma:
    def __init__(self, nome="Conecta Mentor", motor=None):
        self._nome = nome
        self._mentores = {}      # agregação: pessoas e sessões existem fora da plataforma
        self._mentorados = {}
        self._sessoes = {}
        self._motor = motor or MotorDeMatch()   # composição: o motor pertence à plataforma

    @property
    def nome(self):
        return self._nome

    @property
    def motor(self):
        return self._motor

    # ---- cadastros -------------------------------------------------------
    def registrar(self, pessoa):
        if isinstance(pessoa, Mentor):
            self._mentores[pessoa.id] = pessoa
        elif isinstance(pessoa, Mentorado):
            self._mentorados[pessoa.id] = pessoa
        else:
            raise TypeError("Tipo de pessoa desconhecido.")
        return pessoa

    def buscar_mentor(self, mentor_id):
        if mentor_id not in self._mentores:
            raise ValueError(f"Mentor #{mentor_id} não encontrado.")
        return self._mentores[mentor_id]

    def buscar_mentorado(self, mentorado_id):
        if mentorado_id not in self._mentorados:
            raise ValueError(f"Mentorado #{mentorado_id} não encontrado.")
        return self._mentorados[mentorado_id]

    def buscar_sessao(self, sessao_id):
        if sessao_id not in self._sessoes:
            raise ValueError(f"Sessão #{sessao_id} não encontrada.")
        return self._sessoes[sessao_id]

    def listar_mentores(self):
        return list(self._mentores.values())

    def listar_mentorados(self):
        return list(self._mentorados.values())

    def listar_sessoes(self):
        return list(self._sessoes.values())

    # ---- match e agendamento --------------------------------------------
    def sugerir_mentores(self, mentorado_id, limite=3):
        mentorado = self.buscar_mentorado(mentorado_id)
        return self._motor.sugerir(mentorado, self._mentores.values(), limite)

    def agendar(self, mentor_id, mentorado_id, disciplina, horario,
                modalidade="online", detalhe=None):
        mentor = self.buscar_mentor(mentor_id)
        mentorado = self.buscar_mentorado(mentorado_id)
        disc = disciplina if isinstance(disciplina, Disciplina) else Disciplina(disciplina)
        if modalidade == "online":
            sessao = SessaoOnline(mentor, mentorado, disc, horario, detalhe)
        elif modalidade == "presencial":
            sessao = SessaoPresencial(mentor, mentorado, disc, horario, detalhe)
        else:
            raise ValueError("Modalidade deve ser 'online' ou 'presencial'.")
        self._sessoes[sessao.id] = sessao
        return sessao

    def realizar_sessao(self, sessao_id):
        self.buscar_sessao(sessao_id).realizar()

    def cancelar_sessao(self, sessao_id):
        self.buscar_sessao(sessao_id).cancelar()

    def avaliar_sessao(self, sessao_id, nota, comentario=""):
        self.buscar_sessao(sessao_id).avaliar(nota, comentario)

    # ---- relatório ------------------------------------------------------
    def relatorio(self):
        sessoes = list(self._sessoes.values())
        realizadas = [s for s in sessoes if s.status == StatusSessao.REALIZADA]
        notas = [s.avaliacao.nota for s in realizadas if s.avaliacao]
        alunos = {s.mentorado.nome for s in realizadas}
        pedidas = Counter(str(s.disciplina) for s in sessoes)
        linhas = [
            "=" * 54,
            "   RELATÓRIO DE IMPACTO - CONECTA MENTOR",
            "=" * 54,
            f"Mentores cadastrados .......... {len(self._mentores)}",
            f"Mentorados cadastrados ........ {len(self._mentorados)}",
            f"Sessões agendadas (total) ..... {len(sessoes)}",
            f"Sessões realizadas ............ {len(realizadas)}",
            f"Alunos já atendidos ........... {len(alunos)}",
            f"Horas de reforço entregues .... {sum(s.DURACAO_HORAS for s in realizadas)} h",
            f"Nota média das sessões ........ {sum(notas) / len(notas):.1f}/5" if notas
            else "Nota média das sessões ........ -",
            "Disciplinas mais procuradas ... " +
            (", ".join(f"{d} ({n})" for d, n in pedidas.most_common(3)) or "-"),
            "-" * 54,
            "Horas de voluntariado (extensão) por mentor:",
        ]
        for m in self._mentores.values():
            media = m.media_avaliacoes()
            linhas.append(f"   {m.nome}: {m.horas_voluntariado()} h"
                          + (f" | nota {media:.1f}" if media else ""))
        linhas.append("=" * 54)
        return "\n".join(linhas)
