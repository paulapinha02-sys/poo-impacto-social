"""Modelos (classes de domínio) do sistema Prato Cheio - ODS 2 (Fome Zero).

Pilares de POO usados neste módulo:
  * Encapsulamento: atributos privados (_x) expostos por @property.
  * Herança: Restaurante/ONG herdam de Usuario; AlimentoPerecivel/
    AlimentoNaoPerecivel herdam de Alimento.
  * Polimorfismo: resumo() (Usuario) e prioridade()/descricao() (Alimento)
    têm comportamentos diferentes em cada subclasse.
  * Composição: uma Doacao é composta por seus Alimentos (nascem e morrem com ela).
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum


class StatusDoacao(Enum):
    DISPONIVEL = "Disponível"
    RESERVADA = "Reservada"
    RETIRADA = "Retirada"
    EXPIRADA = "Expirada"


# --------------------------------------------------------------------------
# Alimentos (herança + polimorfismo)
# --------------------------------------------------------------------------
class Alimento(ABC):
    """Classe base abstrata de um item de alimento doado."""

    def __init__(self, nome, quantidade_kg, data_validade):
        if not nome or not nome.strip():
            raise ValueError("O alimento precisa de um nome.")
        if quantidade_kg <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        self._nome = nome.strip()
        self._quantidade_kg = float(quantidade_kg)
        self._data_validade = data_validade

    @property
    def nome(self):
        return self._nome

    @property
    def quantidade_kg(self):
        return self._quantidade_kg

    @property
    def data_validade(self):
        return self._data_validade

    def horas_restantes(self, agora=None):
        agora = agora or datetime.now()
        return (self._data_validade - agora).total_seconds() / 3600

    def esta_vencido(self, agora=None):
        return self.horas_restantes(agora) <= 0

    @abstractmethod
    def prioridade(self, agora=None):
        """Retorna 1 (ALTA), 2 (MÉDIA) ou 3 (BAIXA). Cada subclasse decide."""

    @abstractmethod
    def descricao(self):
        """Texto descritivo do item."""


class AlimentoPerecivel(Alimento):
    """Alimento que estraga rápido (ex.: refeições prontas, laticínios)."""

    def __init__(self, nome, quantidade_kg, data_validade, requer_refrigeracao=True):
        super().__init__(nome, quantidade_kg, data_validade)
        self._requer_refrigeracao = requer_refrigeracao

    @property
    def requer_refrigeracao(self):
        return self._requer_refrigeracao

    def prioridade(self, agora=None):
        # Perecível: urgente se restam 12h ou menos.
        return 1 if self.horas_restantes(agora) <= 12 else 2

    def descricao(self):
        frio = " (refrigerar)" if self._requer_refrigeracao else ""
        return f"{self._nome} - {self._quantidade_kg:.1f} kg [perecível{frio}]"


class AlimentoNaoPerecivel(Alimento):
    """Alimento de longa duração (ex.: arroz, feijão, enlatados)."""

    def __init__(self, nome, quantidade_kg, data_validade, embalagem="pacote"):
        super().__init__(nome, quantidade_kg, data_validade)
        self._embalagem = embalagem

    @property
    def embalagem(self):
        return self._embalagem

    def prioridade(self, agora=None):
        # Não perecível: só vira média se restam 7 dias ou menos.
        return 2 if self.horas_restantes(agora) <= 7 * 24 else 3

    def descricao(self):
        return f"{self._nome} - {self._quantidade_kg:.1f} kg [não perecível, {self._embalagem}]"


# --------------------------------------------------------------------------
# Doação e Reserva
# --------------------------------------------------------------------------
class Doacao:
    """Excedente cadastrado por um restaurante. Compõe uma lista de Alimentos."""

    _proximo_id = 1

    def __init__(self, restaurante, itens, limite_retirada, criada_em=None):
        if not itens:
            raise ValueError("Uma doação precisa de pelo menos um alimento.")
        self._id = Doacao._proximo_id
        Doacao._proximo_id += 1
        self._restaurante = restaurante
        self._itens = list(itens)  # composição: itens pertencem à doação
        self._criada_em = criada_em or datetime.now()
        self._limite_retirada = limite_retirada
        self._status = StatusDoacao.DISPONIVEL
        self._reserva = None

    @property
    def id(self):
        return self._id

    @property
    def restaurante(self):
        return self._restaurante

    @property
    def itens(self):
        return tuple(self._itens)  # cópia imutável: protege o encapsulamento

    @property
    def limite_retirada(self):
        return self._limite_retirada

    @property
    def status(self):
        return self._status

    @property
    def reserva(self):
        return self._reserva

    def total_kg(self):
        return sum(i.quantidade_kg for i in self._itens)

    def prioridade(self, agora=None):
        """A doação é tão urgente quanto o seu item mais urgente."""
        return min(i.prioridade(agora) for i in self._itens)

    def esta_expirada(self, agora=None):
        agora = agora or datetime.now()
        return agora >= self._limite_retirada

    def atualizar_status(self, agora=None):
        if self._status in (StatusDoacao.DISPONIVEL, StatusDoacao.RESERVADA) \
                and self.esta_expirada(agora):
            self._status = StatusDoacao.EXPIRADA

    def reservar(self, ong, agora=None):
        self.atualizar_status(agora)
        if self._status != StatusDoacao.DISPONIVEL:
            raise ValueError(f"Doação #{self._id} não está disponível ({self._status.value}).")
        self._status = StatusDoacao.RESERVADA
        self._reserva = Reserva(self, ong, agora)
        return self._reserva

    def confirmar_retirada(self, agora=None):
        self.atualizar_status(agora)
        if self._status != StatusDoacao.RESERVADA:
            raise ValueError(f"Doação #{self._id} não está reservada ({self._status.value}).")
        self._status = StatusDoacao.RETIRADA
        self._reserva.confirmar(agora)

    def __str__(self):
        urgencia = {1: "ALTA", 2: "MÉDIA", 3: "BAIXA"}[self.prioridade()]
        itens = "; ".join(i.descricao() for i in self._itens)
        return (f"Doação #{self._id} | {self._restaurante.nome} | {self.total_kg():.1f} kg | "
                f"urgência {urgencia} | {self._status.value}\n      Itens: {itens}")


class Reserva:
    """Vínculo entre uma Doacao e a ONG que vai retirá-la."""

    def __init__(self, doacao, ong, data_reserva=None):
        self._doacao = doacao
        self._ong = ong
        self._data_reserva = data_reserva or datetime.now()
        self._data_retirada = None

    @property
    def doacao(self):
        return self._doacao

    @property
    def ong(self):
        return self._ong

    @property
    def data_retirada(self):
        return self._data_retirada

    def confirmar(self, agora=None):
        self._data_retirada = agora or datetime.now()


# --------------------------------------------------------------------------
# Usuários (herança + polimorfismo)
# --------------------------------------------------------------------------
class Usuario(ABC):
    """Classe base abstrata dos atores da plataforma."""

    _proximo_id = 1

    def __init__(self, nome, email, cidade):
        if not nome or not nome.strip():
            raise ValueError("O nome é obrigatório.")
        if "@" not in email:
            raise ValueError("E-mail inválido.")
        self._id = Usuario._proximo_id
        Usuario._proximo_id += 1
        self._nome = nome.strip()
        self._email = email
        self._cidade = cidade.strip()

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

    @abstractmethod
    def resumo(self):
        """Cada tipo de usuário se apresenta de um jeito (polimorfismo)."""

    def __str__(self):
        return self.resumo()


class Restaurante(Usuario):
    """Doador de excedente de alimentos."""

    def __init__(self, nome, email, cidade, cnpj):
        super().__init__(nome, email, cidade)
        self._cnpj = cnpj
        self._doacoes = []

    @property
    def cnpj(self):
        return self._cnpj

    @property
    def doacoes(self):
        return tuple(self._doacoes)

    def cadastrar_doacao(self, itens, horas_para_retirada, agora=None):
        agora = agora or datetime.now()
        limite = agora + timedelta(hours=horas_para_retirada)
        doacao = Doacao(self, itens, limite, agora)
        self._doacoes.append(doacao)
        return doacao

    def total_kg_doado(self):
        return sum(d.total_kg() for d in self._doacoes if d.status == StatusDoacao.RETIRADA)

    def resumo(self):
        return (f"[Restaurante #{self._id}] {self._nome} - {self._cidade} "
                f"(CNPJ {self._cnpj}) | {len(self._doacoes)} doação(ões) cadastrada(s)")


class ONG(Usuario):
    """Receptora das doações; distribui os alimentos a famílias atendidas."""

    def __init__(self, nome, email, cidade, capacidade_kg, familias_atendidas):
        super().__init__(nome, email, cidade)
        if capacidade_kg <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        self._capacidade_kg = float(capacidade_kg)
        self._familias_atendidas = familias_atendidas
        self._reservas = []

    @property
    def capacidade_kg(self):
        return self._capacidade_kg

    @property
    def familias_atendidas(self):
        return self._familias_atendidas

    @property
    def reservas(self):
        return tuple(self._reservas)

    def kg_em_reserva(self):
        """Quantidade já reservada e ainda não retirada (ocupa a capacidade)."""
        return sum(r.doacao.total_kg() for r in self._reservas
                   if r.doacao.status == StatusDoacao.RESERVADA)

    def reservar(self, doacao, agora=None):
        if self.kg_em_reserva() + doacao.total_kg() > self._capacidade_kg:
            raise ValueError(
                f"{self._nome} não tem capacidade: {self.kg_em_reserva():.1f} kg já reservados "
                f"de {self._capacidade_kg:.1f} kg.")
        reserva = doacao.reservar(self, agora)
        self._reservas.append(reserva)
        return reserva

    def total_kg_recebido(self):
        return sum(r.doacao.total_kg() for r in self._reservas
                   if r.doacao.status == StatusDoacao.RETIRADA)

    def resumo(self):
        return (f"[ONG #{self._id}] {self._nome} - {self._cidade} | capacidade "
                f"{self._capacidade_kg:.0f} kg | {self._familias_atendidas} famílias atendidas")
