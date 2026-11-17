"""Modelos de domínio do EcoPonto - ODS 12 (Consumo e Produção Responsáveis).

Pilares de POO usados neste módulo:
  * Encapsulamento: atributos privados (_x) + @property; regras de saldo, capacidade
    e estoque protegidas dentro das próprias classes.
  * Herança: Cidadao e Parceiro herdam de Usuario; Celular, Bateria, Computador e
    Eletrodomestico herdam de ItemEletronico.
  * Polimorfismo: calcular_pontos(), destino() e categoria() mudam em cada tipo de item.
  * Composição: uma Entrega é composta de seus ItemEletronico; um Parceiro possui
    suas Recompensas.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class DestinoFinal(Enum):
    RECONDICIONAMENTO = "Recondicionamento / reúso"
    RECICLAGEM = "Reciclagem de materiais"
    RESIDUO_PERIGOSO = "Descarte especial (resíduo perigoso)"


# --------------------------------------------------------------------------
# Itens eletrônicos (herança + polimorfismo)
# --------------------------------------------------------------------------
class ItemEletronico(ABC):
    """Classe base abstrata de um item entregue para descarte correto."""

    def __init__(self, descricao, peso_kg):
        if not descricao or not descricao.strip():
            raise ValueError("O item precisa de uma descrição.")
        if peso_kg <= 0:
            raise ValueError("O peso deve ser maior que zero.")
        self._descricao = descricao.strip()
        self._peso_kg = float(peso_kg)

    @property
    def descricao(self):
        return self._descricao

    @property
    def peso_kg(self):
        return self._peso_kg

    @abstractmethod
    def categoria(self):
        """Nome da categoria (usado para saber o que cada ponto aceita)."""

    @abstractmethod
    def calcular_pontos(self):
        """Pontos que o item vale. Cada tipo tem sua regra (polimorfismo)."""

    @abstractmethod
    def destino(self):
        """Para onde o item vai (DestinoFinal)."""

    def __str__(self):
        return (f"{self.categoria()}: {self._descricao} ({self._peso_kg:.2f} kg) "
                f"= {self.calcular_pontos()} pts -> {self.destino().value}")


class Celular(ItemEletronico):
    """Celular funcional vale mais, pois pode ser recondicionado e doado."""

    def __init__(self, descricao, peso_kg, funcional=False):
        super().__init__(descricao, peso_kg)
        self._funcional = funcional

    @property
    def funcional(self):
        return self._funcional

    def categoria(self):
        return "Celular"

    def calcular_pontos(self):
        return 70 if self._funcional else 40

    def destino(self):
        return DestinoFinal.RECONDICIONAMENTO if self._funcional else DestinoFinal.RECICLAGEM


class Bateria(ItemEletronico):
    """Pilhas e baterias são resíduo perigoso: o descarte correto vale mais pontos."""

    def __init__(self, descricao, peso_kg, tipo="íon-lítio"):
        super().__init__(descricao, peso_kg)
        self._tipo = tipo

    @property
    def tipo(self):
        return self._tipo

    def categoria(self):
        return "Bateria"

    def calcular_pontos(self):
        return max(20, round(self._peso_kg * 300))

    def destino(self):
        return DestinoFinal.RESIDUO_PERIGOSO


class Computador(ItemEletronico):
    """Computadores e notebooks: 20 pontos fixos + 25 por kg."""

    def __init__(self, descricao, peso_kg, notebook=True):
        super().__init__(descricao, peso_kg)
        self._notebook = notebook

    @property
    def notebook(self):
        return self._notebook

    def categoria(self):
        return "Computador"

    def calcular_pontos(self):
        return round(20 + self._peso_kg * 25)

    def destino(self):
        return DestinoFinal.RECICLAGEM


class Eletrodomestico(ItemEletronico):
    """Eletrodomésticos pequenos: 10 pontos por kg (mínimo 10)."""

    def categoria(self):
        return "Eletrodoméstico"

    def calcular_pontos(self):
        return max(10, round(self._peso_kg * 10))

    def destino(self):
        return DestinoFinal.RECICLAGEM


# --------------------------------------------------------------------------
# Recompensas e resgates
# --------------------------------------------------------------------------
class Recompensa:
    """Benefício oferecido por um parceiro em troca de pontos."""

    _proximo_id = 1

    def __init__(self, parceiro, nome, custo_pontos, estoque):
        if custo_pontos <= 0 or estoque < 0:
            raise ValueError("Custo deve ser positivo e estoque não pode ser negativo.")
        self._id = Recompensa._proximo_id
        Recompensa._proximo_id += 1
        self._parceiro = parceiro
        self._nome = nome
        self._custo_pontos = custo_pontos
        self._estoque = estoque

    @property
    def id(self):
        return self._id

    @property
    def parceiro(self):
        return self._parceiro

    @property
    def nome(self):
        return self._nome

    @property
    def custo_pontos(self):
        return self._custo_pontos

    @property
    def estoque(self):
        return self._estoque

    def retirar_do_estoque(self):
        if self._estoque <= 0:
            raise ValueError(f"A recompensa '{self._nome}' está esgotada.")
        self._estoque -= 1

    def __str__(self):
        return (f"Recompensa #{self._id}: {self._nome} - {self._custo_pontos} pts "
                f"({self._parceiro.nome}) | estoque: {self._estoque}")


class Resgate:
    def __init__(self, cidadao, recompensa, data=None):
        self._cidadao = cidadao
        self._recompensa = recompensa
        self._data = data or datetime.now()

    @property
    def cidadao(self):
        return self._cidadao

    @property
    def recompensa(self):
        return self._recompensa

    @property
    def data(self):
        return self._data


# --------------------------------------------------------------------------
# Usuários (herança + polimorfismo)
# --------------------------------------------------------------------------
class Usuario(ABC):
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
        """Apresentação do usuário (polimorfismo)."""

    def __str__(self):
        return self.resumo()


class Cidadao(Usuario):
    """Pessoa que entrega eletrônicos e acumula pontos."""

    # (pontos acumulados mínimos, nível, multiplicador de bônus)
    NIVEIS = [(500, "Ouro", 1.2), (200, "Prata", 1.1), (0, "Bronze", 1.0)]

    def __init__(self, nome, email, cidade):
        super().__init__(nome, email, cidade)
        self._saldo = 0
        self._acumulados = 0
        self._entregas = []
        self._resgates = []

    @property
    def saldo(self):
        return self._saldo

    @property
    def acumulados(self):
        return self._acumulados

    @property
    def entregas(self):
        return tuple(self._entregas)

    @property
    def resgates(self):
        return tuple(self._resgates)

    def _faixa(self):
        return next(n for n in self.NIVEIS if self._acumulados >= n[0])

    def nivel(self):
        return self._faixa()[1]

    def multiplicador(self):
        return self._faixa()[2]

    def creditar(self, pontos):
        if pontos <= 0:
            raise ValueError("Os pontos a creditar devem ser positivos.")
        self._saldo += pontos
        self._acumulados += pontos

    def debitar(self, pontos):
        if pontos > self._saldo:
            raise ValueError(f"Saldo insuficiente: {self._nome} tem {self._saldo} pts e precisa de {pontos}.")
        self._saldo -= pontos

    def registrar_entrega(self, entrega):
        self._entregas.append(entrega)

    def registrar_resgate(self, resgate):
        self._resgates.append(resgate)

    def total_kg_entregue(self):
        return sum(e.peso_total() for e in self._entregas)

    def resumo(self):
        return (f"[Cidadão #{self._id}] {self._nome} - {self._cidade} | nível {self.nivel()} | "
                f"saldo {self._saldo} pts | {self.total_kg_entregue():.2f} kg entregues")


class Parceiro(Usuario):
    """Comércio local que oferece recompensas em troca de pontos."""

    def __init__(self, nome, email, cidade, ramo):
        super().__init__(nome, email, cidade)
        self._ramo = ramo
        self._recompensas = []   # composição: as recompensas pertencem ao parceiro

    @property
    def ramo(self):
        return self._ramo

    @property
    def recompensas(self):
        return tuple(self._recompensas)

    def cadastrar_recompensa(self, nome, custo_pontos, estoque):
        r = Recompensa(self, nome, custo_pontos, estoque)
        self._recompensas.append(r)
        return r

    def resumo(self):
        return (f"[Parceiro #{self._id}] {self._nome} ({self._ramo}) - {self._cidade} | "
                f"{len(self._recompensas)} recompensa(s)")


# --------------------------------------------------------------------------
# Ponto de coleta e Entrega
# --------------------------------------------------------------------------
class PontoDeColeta:
    """Local físico que recebe eletrônicos, com capacidade e categorias aceitas."""

    _proximo_id = 1

    def __init__(self, nome, endereco, cidade, capacidade_kg, categorias_aceitas):
        if capacidade_kg <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        self._id = PontoDeColeta._proximo_id
        PontoDeColeta._proximo_id += 1
        self._nome = nome
        self._endereco = endereco
        self._cidade = cidade
        self._capacidade_kg = float(capacidade_kg)
        self._categorias = frozenset(categorias_aceitas)
        self._estoque_kg = 0.0
        self._total_encaminhado_kg = 0.0

    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @property
    def cidade(self):
        return self._cidade

    @property
    def capacidade_kg(self):
        return self._capacidade_kg

    @property
    def estoque_kg(self):
        return self._estoque_kg

    @property
    def total_encaminhado_kg(self):
        return self._total_encaminhado_kg

    @property
    def categorias_aceitas(self):
        return self._categorias

    def validar_recebimento(self, itens):
        for item in itens:
            if item.categoria() not in self._categorias:
                raise ValueError(f"O ponto '{self._nome}' não aceita {item.categoria()}.")
        peso = sum(i.peso_kg for i in itens)
        if self._estoque_kg + peso > self._capacidade_kg:
            livre = self._capacidade_kg - self._estoque_kg
            raise ValueError(f"O ponto '{self._nome}' não tem espaço: restam {livre:.2f} kg e a "
                             f"entrega pesa {peso:.2f} kg.")

    def receber(self, itens):
        self.validar_recebimento(itens)
        self._estoque_kg += sum(i.peso_kg for i in itens)

    def coletar(self):
        """A cooperativa/recicladora retira o material; o estoque é zerado."""
        retirado = self._estoque_kg
        self._total_encaminhado_kg += retirado
        self._estoque_kg = 0.0
        return retirado

    def __str__(self):
        return (f"[Ponto #{self._id}] {self._nome} - {self._endereco}, {self._cidade} | "
                f"{self._estoque_kg:.2f}/{self._capacidade_kg:.0f} kg | aceita: "
                f"{', '.join(sorted(self._categorias))}")


class Entrega:
    """Registro de uma entrega de itens por um cidadão. Compõe seus itens."""

    def __init__(self, cidadao, ponto, itens, data=None):
        if not itens:
            raise ValueError("A entrega precisa de pelo menos um item.")
        ponto.validar_recebimento(itens)             # falha antes de alterar qualquer estado
        self._cidadao = cidadao
        self._ponto = ponto
        self._itens = list(itens)                    # composição
        self._data = data or datetime.now()
        base = sum(i.calcular_pontos() for i in self._itens)   # polimorfismo
        self._pontos_base = base
        self._bonus = round(base * cidadao.multiplicador()) - base
        ponto.receber(self._itens)
        cidadao.creditar(base + self._bonus)
        cidadao.registrar_entrega(self)

    @property
    def cidadao(self):
        return self._cidadao

    @property
    def ponto(self):
        return self._ponto

    @property
    def itens(self):
        return tuple(self._itens)

    @property
    def pontos_base(self):
        return self._pontos_base

    @property
    def bonus(self):
        return self._bonus

    @property
    def pontos_total(self):
        return self._pontos_base + self._bonus

    def peso_total(self):
        return sum(i.peso_kg for i in self._itens)

    def __str__(self):
        linhas = "\n".join(f"      - {i}" for i in self._itens)
        return (f"{self._cidadao.nome} entregou {self.peso_total():.2f} kg em '{self._ponto.nome}' "
                f"-> {self._pontos_base} pts + bônus {self._bonus} = {self.pontos_total} pts\n{linhas}")
