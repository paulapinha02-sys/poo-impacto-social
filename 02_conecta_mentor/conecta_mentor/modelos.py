"""Modelos de domínio do Conecta Mentor - ODS 4 (Educação de Qualidade).

Pilares de POO usados neste módulo:
  * Encapsulamento: atributos privados (_x) + @property; objetos de valor imutáveis
    (Disciplina, Horario, Avaliacao são dataclasses "frozen").
  * Herança: Mentor e Mentorado herdam de Pessoa; SessaoOnline e SessaoPresencial
    herdam de Sessao.
  * Polimorfismo: papel()/resumo() (Pessoa) e como_participar() (Sessao).
  * Composição: Pessoa possui seus Horarios; Sessao possui sua Avaliacao.
"""
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn").lower()


# --------------------------------------------------------------------------
# Objetos de valor (imutáveis)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Disciplina:
    nome: str

    def __post_init__(self):
        if not self.nome or not self.nome.strip():
            raise ValueError("A disciplina precisa de um nome.")
        object.__setattr__(self, "nome", self.nome.strip().title())

    def __str__(self):
        return self.nome


@dataclass(frozen=True, order=True)
class Horario:
    """Horário semanal de 1 hora (ex.: terça às 14h)."""
    dia: int   # 0 = segunda ... 6 = domingo
    hora: int  # 6 a 21

    def __post_init__(self):
        if not 0 <= self.dia <= 6:
            raise ValueError("Dia inválido (use 0 a 6).")
        if not 6 <= self.hora <= 21:
            raise ValueError("Hora inválida (use entre 6 e 21).")

    @classmethod
    def de_texto(cls, texto):
        """Converte 'ter 14' ou 'terça 14' em Horario."""
        partes = texto.split()
        if len(partes) != 2 or not partes[1].isdigit():
            raise ValueError(f"Horário inválido: '{texto}'. Use o formato 'ter 14'.")
        for i, nome in enumerate(DIAS):
            if _sem_acento(nome).startswith(_sem_acento(partes[0])[:3]):
                return cls(i, int(partes[1]))
        raise ValueError(f"Dia da semana inválido: '{partes[0]}'.")

    def __str__(self):
        return f"{DIAS[self.dia]} {self.hora:02d}h"


@dataclass(frozen=True)
class Avaliacao:
    nota: int
    comentario: str = ""

    def __post_init__(self):
        if not 1 <= self.nota <= 5:
            raise ValueError("A nota deve ser de 1 a 5.")


class StatusSessao(Enum):
    AGENDADA = "Agendada"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"


# --------------------------------------------------------------------------
# Pessoas (herança + polimorfismo)
# --------------------------------------------------------------------------
class Pessoa(ABC):
    """Classe base abstrata: dados e agenda comuns a mentores e mentorados."""

    _proximo_id = 1

    def __init__(self, nome, email, cidade):
        if not nome or not nome.strip():
            raise ValueError("O nome é obrigatório.")
        if "@" not in email:
            raise ValueError("E-mail inválido.")
        self._id = Pessoa._proximo_id
        Pessoa._proximo_id += 1
        self._nome = nome.strip()
        self._email = email
        self._cidade = cidade.strip()
        self._disponibilidades = set()  # composição: horários pertencem à pessoa
        self._sessoes = []

    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @property
    def email(self):
        return self._email

    @property
    def cidade(self):
        return self._cidade

    @property
    def disponibilidades(self):
        return frozenset(self._disponibilidades)

    @property
    def sessoes(self):
        return tuple(self._sessoes)

    def adicionar_disponibilidade(self, horario):
        self._disponibilidades.add(horario)

    def reservar_horario(self, horario):
        if horario not in self._disponibilidades:
            raise ValueError(f"{self._nome} não está disponível em {horario}.")
        self._disponibilidades.remove(horario)

    def liberar_horario(self, horario):
        self._disponibilidades.add(horario)

    def registrar_sessao(self, sessao):
        self._sessoes.append(sessao)

    @abstractmethod
    def papel(self):
        """Nome do papel na plataforma (cada subclasse responde o seu)."""

    @abstractmethod
    def resumo(self):
        """Apresentação da pessoa (polimorfismo)."""

    def __str__(self):
        return self.resumo()


class Mentor(Pessoa):
    """Universitário voluntário que ensina disciplinas."""

    def __init__(self, nome, email, cidade, curso, semestre, limite_sessoes=3):
        super().__init__(nome, email, cidade)
        if limite_sessoes < 1:
            raise ValueError("O limite de sessões deve ser pelo menos 1.")
        self._curso = curso
        self._semestre = semestre
        self._limite_sessoes = limite_sessoes
        self._disciplinas = set()

    @property
    def curso(self):
        return self._curso

    @property
    def disciplinas(self):
        return frozenset(self._disciplinas)

    @property
    def limite_sessoes(self):
        return self._limite_sessoes

    def adicionar_disciplina(self, disciplina):
        self._disciplinas.add(disciplina)

    def ensina(self, disciplina):
        return disciplina in self._disciplinas

    def sessoes_agendadas(self):
        return sum(1 for s in self._sessoes if s.status == StatusSessao.AGENDADA)

    def pode_aceitar(self):
        return self.sessoes_agendadas() < self._limite_sessoes

    def horas_voluntariado(self):
        """Horas de extensão acumuladas (sessões realizadas)."""
        return sum(s.DURACAO_HORAS for s in self._sessoes if s.status == StatusSessao.REALIZADA)

    def media_avaliacoes(self):
        notas = [s.avaliacao.nota for s in self._sessoes if s.avaliacao]
        return sum(notas) / len(notas) if notas else None

    def papel(self):
        return "Mentor"

    def resumo(self):
        ensina = ", ".join(sorted(d.nome for d in self._disciplinas)) or "-"
        return (f"[Mentor #{self._id}] {self._nome} - {self._curso}, {self._semestre}º sem. | "
                f"ensina: {ensina}")


class Mentorado(Pessoa):
    """Aluno da rede pública que busca reforço escolar."""

    def __init__(self, nome, email, cidade, escola, serie):
        super().__init__(nome, email, cidade)
        self._escola = escola
        self._serie = serie
        self._dificuldades = set()

    @property
    def escola(self):
        return self._escola

    @property
    def serie(self):
        return self._serie

    @property
    def dificuldades(self):
        return frozenset(self._dificuldades)

    def adicionar_dificuldade(self, disciplina):
        self._dificuldades.add(disciplina)

    def papel(self):
        return "Mentorado"

    def resumo(self):
        dif = ", ".join(sorted(d.nome for d in self._dificuldades)) or "-"
        return (f"[Mentorado #{self._id}] {self._nome} - {self._serie}, {self._escola} | "
                f"dificuldades: {dif}")


# --------------------------------------------------------------------------
# Sessões (herança + polimorfismo)
# --------------------------------------------------------------------------
class Sessao(ABC):
    """Sessão de reforço entre um Mentor e um Mentorado. Base abstrata."""

    DURACAO_HORAS = 1
    _proximo_id = 1

    def __init__(self, mentor, mentorado, disciplina, horario):
        if not mentor.ensina(disciplina):
            raise ValueError(f"{mentor.nome} não ensina {disciplina}.")
        if not mentor.pode_aceitar():
            plural = "sessão" if mentor.limite_sessoes == 1 else "sessões"
            raise ValueError(f"{mentor.nome} atingiu o limite de {mentor.limite_sessoes} {plural} agendada(s).")
        # reserva os horários dos dois lados (lança erro se algum não estiver livre)
        if horario not in mentor.disponibilidades:
            raise ValueError(f"{mentor.nome} não está disponível em {horario}.")
        if horario not in mentorado.disponibilidades:
            raise ValueError(f"{mentorado.nome} não está disponível em {horario}.")
        mentor.reservar_horario(horario)
        mentorado.reservar_horario(horario)

        self._id = Sessao._proximo_id
        Sessao._proximo_id += 1
        self._mentor = mentor
        self._mentorado = mentorado
        self._disciplina = disciplina
        self._horario = horario
        self._status = StatusSessao.AGENDADA
        self._avaliacao = None  # composição: a avaliação pertence à sessão
        mentor.registrar_sessao(self)
        mentorado.registrar_sessao(self)

    @property
    def id(self):
        return self._id

    @property
    def mentor(self):
        return self._mentor

    @property
    def mentorado(self):
        return self._mentorado

    @property
    def disciplina(self):
        return self._disciplina

    @property
    def horario(self):
        return self._horario

    @property
    def status(self):
        return self._status

    @property
    def avaliacao(self):
        return self._avaliacao

    def realizar(self):
        if self._status != StatusSessao.AGENDADA:
            raise ValueError(f"Sessão #{self._id} não está agendada ({self._status.value}).")
        self._status = StatusSessao.REALIZADA

    def cancelar(self):
        if self._status != StatusSessao.AGENDADA:
            raise ValueError(f"Sessão #{self._id} não pode ser cancelada ({self._status.value}).")
        self._status = StatusSessao.CANCELADA
        self._mentor.liberar_horario(self._horario)
        self._mentorado.liberar_horario(self._horario)

    def avaliar(self, nota, comentario=""):
        if self._status != StatusSessao.REALIZADA:
            raise ValueError("Só é possível avaliar sessões realizadas.")
        if self._avaliacao is not None:
            raise ValueError("Esta sessão já foi avaliada.")
        self._avaliacao = Avaliacao(nota, comentario)

    @abstractmethod
    def como_participar(self):
        """Instruções de acesso: cada modalidade informa de um jeito."""

    def __str__(self):
        return (f"Sessão #{self._id} | {self._disciplina} | {self._mentor.nome} -> "
                f"{self._mentorado.nome} | {self._horario} | {self._status.value}\n"
                f"      {self.como_participar()}")


class SessaoOnline(Sessao):
    def __init__(self, mentor, mentorado, disciplina, horario, link=None):
        super().__init__(mentor, mentorado, disciplina, horario)
        self._link = link or f"https://meet.conectamentor.org/sala-{self._id}"

    @property
    def link(self):
        return self._link

    def como_participar(self):
        return f"Online: acesse {self._link}"


class SessaoPresencial(Sessao):
    def __init__(self, mentor, mentorado, disciplina, horario, local):
        if not local or not local.strip():
            raise ValueError("Informe o local da sessão presencial.")
        super().__init__(mentor, mentorado, disciplina, horario)
        self._local = local.strip()

    @property
    def local(self):
        return self._local

    def como_participar(self):
        return f"Presencial: compareça em {self._local}"
