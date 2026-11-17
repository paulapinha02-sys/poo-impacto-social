"""Algoritmo de match entre Mentor e Mentorado (padrão Strategy).

Cada CriterioMatch dá uma nota de 0 a 1 de um jeito diferente (polimorfismo).
O MotorDeMatch combina os critérios com pesos.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


class CriterioMatch(ABC):
    def __init__(self, peso):
        if peso <= 0:
            raise ValueError("O peso deve ser positivo.")
        self._peso = peso

    @property
    def peso(self):
        return self._peso

    @property
    @abstractmethod
    def nome(self):
        ...

    @abstractmethod
    def pontuar(self, mentor, mentorado):
        """Retorna um valor entre 0 e 1."""


class CriterioDisciplina(CriterioMatch):
    """Quanto das dificuldades do aluno o mentor consegue cobrir."""
    nome = "disciplinas"

    def pontuar(self, mentor, mentorado):
        dificuldades = mentorado.dificuldades
        if not dificuldades:
            return 0.0
        return len(mentor.disciplinas & dificuldades) / len(dificuldades)


class CriterioHorario(CriterioMatch):
    """Quantos horários livres em comum (3 ou mais já é nota máxima)."""
    nome = "horários"

    def pontuar(self, mentor, mentorado):
        comuns = len(mentor.disponibilidades & mentorado.disponibilidades)
        return min(comuns, 3) / 3


class CriterioAvaliacao(CriterioMatch):
    """Reputação do mentor. Mentor novo recebe nota neutra (0,5) para não ser prejudicado."""
    nome = "avaliações"

    def pontuar(self, mentor, mentorado):
        media = mentor.media_avaliacoes()
        return 0.5 if media is None else media / 5


@dataclass(frozen=True)
class Sugestao:
    mentor: object
    pontuacao: float
    disciplinas_comuns: tuple
    horarios_comuns: tuple


class MotorDeMatch:
    def __init__(self, criterios=None):
        self._criterios = list(criterios) if criterios else [
            CriterioDisciplina(5), CriterioHorario(3), CriterioAvaliacao(2)]
        self._soma_pesos = sum(c.peso for c in self._criterios)

    @property
    def criterios(self):
        return tuple(self._criterios)

    def sugerir(self, mentorado, mentores, limite=3):
        sugestoes = []
        for mentor in mentores:
            disc = mentor.disciplinas & mentorado.dificuldades
            hor = mentor.disponibilidades & mentorado.disponibilidades
            # só é viável se ensina algo que o aluno precisa, em horário comum, e tem vaga
            if not disc or not hor or not mentor.pode_aceitar():
                continue
            nota = sum(c.peso * c.pontuar(mentor, mentorado) for c in self._criterios)
            sugestoes.append(Sugestao(mentor, nota / self._soma_pesos,
                                      tuple(sorted(d.nome for d in disc)), tuple(sorted(hor))))
        sugestoes.sort(key=lambda s: s.pontuacao, reverse=True)
        return sugestoes[:limite]
