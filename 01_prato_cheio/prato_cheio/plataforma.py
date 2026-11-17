"""Plataforma (controlador central) e RelatorioImpacto do Prato Cheio."""
from datetime import datetime

from .modelos import ONG, Restaurante, StatusDoacao, Usuario


class RelatorioImpacto:
    """Consolida os resultados sociais e ambientais da plataforma."""

    # Estimativa usada só para dar ideia de impacto: ~0,4 kg de comida por refeição.
    KG_POR_REFEICAO = 0.4

    def __init__(self, doacoes, usuarios):
        retiradas = [d for d in doacoes if d.status == StatusDoacao.RETIRADA]
        expiradas = [d for d in doacoes if d.status == StatusDoacao.EXPIRADA]
        self._kg_redistribuido = sum(d.total_kg() for d in retiradas)
        self._kg_perdido = sum(d.total_kg() for d in expiradas)
        self._total_doacoes = len(doacoes)
        self._ongs_atendidas = {d.reserva.ong.nome for d in retiradas}
        self._restaurantes_ativos = {d.restaurante.nome for d in doacoes}
        self._familias = sum(u.familias_atendidas for u in usuarios
                             if isinstance(u, ONG) and u.nome in self._ongs_atendidas)

    @property
    def kg_redistribuido(self):
        return self._kg_redistribuido

    @property
    def refeicoes_estimadas(self):
        return int(self._kg_redistribuido / self.KG_POR_REFEICAO)

    def gerar_texto(self):
        total_kg = self._kg_redistribuido + self._kg_perdido
        taxa = (self._kg_redistribuido / total_kg * 100) if total_kg else 0
        return "\n".join([
            "=" * 54,
            "   RELATÓRIO DE IMPACTO - PRATO CHEIO",
            "=" * 54,
            f"Doações cadastradas ........... {self._total_doacoes}",
            f"Restaurantes participantes .... {len(self._restaurantes_ativos)}",
            f"ONGs que receberam alimento ... {len(self._ongs_atendidas)}",
            f"Alimento redistribuído ........ {self._kg_redistribuido:.1f} kg",
            f"Refeições estimadas ........... ~{self.refeicoes_estimadas}"
            f" (considerando {self.KG_POR_REFEICAO} kg/refeição)",
            f"Alimento perdido (expirou) .... {self._kg_perdido:.1f} kg",
            f"Taxa de aproveitamento ........ {taxa:.0f}%",
            f"Famílias nas ONGs atendidas ... {self._familias}",
            "=" * 54,
        ])


class Plataforma:
    """Ponto de entrada do sistema: cadastra usuários e coordena as doações."""

    def __init__(self, nome="Prato Cheio"):
        self._nome = nome
        self._usuarios = {}   # agregação: usuários existem independente da plataforma
        self._doacoes = {}

    @property
    def nome(self):
        return self._nome

    def registrar_usuario(self, usuario: Usuario):
        self._usuarios[usuario.id] = usuario
        return usuario

    def buscar_usuario(self, usuario_id, tipo=Usuario):
        usuario = self._usuarios.get(usuario_id)
        if not isinstance(usuario, tipo):
            raise ValueError(f"{tipo.__name__} #{usuario_id} não encontrado.")
        return usuario

    def listar_usuarios(self, tipo=Usuario):
        return [u for u in self._usuarios.values() if isinstance(u, tipo)]

    def publicar_doacao(self, restaurante_id, itens, horas_para_retirada, agora=None):
        restaurante = self.buscar_usuario(restaurante_id, Restaurante)
        doacao = restaurante.cadastrar_doacao(itens, horas_para_retirada, agora)
        self._doacoes[doacao.id] = doacao
        return doacao

    def buscar_doacao(self, doacao_id):
        if doacao_id not in self._doacoes:
            raise ValueError(f"Doação #{doacao_id} não encontrada.")
        return self._doacoes[doacao_id]

    def atualizar_expiradas(self, agora=None):
        for doacao in self._doacoes.values():
            doacao.atualizar_status(agora)

    def listar_disponiveis(self, cidade=None, agora=None):
        """Doações disponíveis, das mais urgentes para as menos urgentes."""
        self.atualizar_expiradas(agora)
        disponiveis = [d for d in self._doacoes.values()
                       if d.status == StatusDoacao.DISPONIVEL
                       and (cidade is None or d.restaurante.cidade.lower() == cidade.lower())]
        return sorted(disponiveis, key=lambda d: (d.prioridade(agora), d.limite_retirada))

    def reservar(self, ong_id, doacao_id, agora=None):
        ong = self.buscar_usuario(ong_id, ONG)
        return ong.reservar(self.buscar_doacao(doacao_id), agora)

    def confirmar_retirada(self, doacao_id, agora=None):
        self.buscar_doacao(doacao_id).confirmar_retirada(agora)

    def gerar_relatorio(self):
        return RelatorioImpacto(list(self._doacoes.values()), list(self._usuarios.values()))
