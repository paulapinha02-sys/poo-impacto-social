"""Plataforma EcoPonto: coordena cadastros, entregas, resgates e relatório."""
from collections import Counter

from .modelos import Cidadao, Parceiro, Entrega, PontoDeColeta, Resgate, Usuario


class Plataforma:
    def __init__(self, nome="EcoPonto"):
        self._nome = nome
        self._usuarios = {}   # agregação: usuários, pontos e entregas existem fora da plataforma
        self._pontos = {}
        self._entregas = []
        self._resgates = []

    @property
    def nome(self):
        return self._nome

    # ---- cadastros -------------------------------------------------------
    def registrar_usuario(self, usuario: Usuario):
        self._usuarios[usuario.id] = usuario
        return usuario

    def registrar_ponto(self, ponto: PontoDeColeta):
        self._pontos[ponto.id] = ponto
        return ponto

    def buscar_usuario(self, usuario_id, tipo=Usuario):
        u = self._usuarios.get(usuario_id)
        if not isinstance(u, tipo):
            raise ValueError(f"{tipo.__name__} #{usuario_id} não encontrado.")
        return u

    def buscar_ponto(self, ponto_id):
        if ponto_id not in self._pontos:
            raise ValueError(f"Ponto de coleta #{ponto_id} não encontrado.")
        return self._pontos[ponto_id]

    def listar_usuarios(self, tipo=Usuario):
        return [u for u in self._usuarios.values() if isinstance(u, tipo)]

    def listar_pontos(self):
        return list(self._pontos.values())

    def listar_recompensas(self):
        return [r for p in self.listar_usuarios(Parceiro) for r in p.recompensas]

    def buscar_recompensa(self, recompensa_id):
        for r in self.listar_recompensas():
            if r.id == recompensa_id:
                return r
        raise ValueError(f"Recompensa #{recompensa_id} não encontrada.")

    # ---- operações -------------------------------------------------------
    def entregar(self, cidadao_id, ponto_id, itens, data=None):
        cidadao = self.buscar_usuario(cidadao_id, Cidadao)
        ponto = self.buscar_ponto(ponto_id)
        entrega = Entrega(cidadao, ponto, itens, data)
        self._entregas.append(entrega)
        return entrega

    def resgatar(self, cidadao_id, recompensa_id, data=None):
        cidadao = self.buscar_usuario(cidadao_id, Cidadao)
        recompensa = self.buscar_recompensa(recompensa_id)
        if recompensa.estoque <= 0:
            raise ValueError(f"A recompensa '{recompensa.nome}' está esgotada.")
        cidadao.debitar(recompensa.custo_pontos)     # lança erro se faltar saldo
        recompensa.retirar_do_estoque()
        resgate = Resgate(cidadao, recompensa, data)
        cidadao.registrar_resgate(resgate)
        self._resgates.append(resgate)
        return resgate

    def coletar_ponto(self, ponto_id):
        return self.buscar_ponto(ponto_id).coletar()

    # ---- relatório ------------------------------------------------------
    def relatorio(self):
        kg_por_destino = Counter()
        kg_por_categoria = Counter()
        pontos_emitidos = 0
        for e in self._entregas:
            pontos_emitidos += e.pontos_total
            for item in e.itens:
                kg_por_destino[item.destino()] += item.peso_kg
                kg_por_categoria[item.categoria()] += item.peso_kg
        total_kg = sum(kg_por_destino.values())
        pontos_gastos = sum(r.recompensa.custo_pontos for r in self._resgates)
        ranking = sorted(self.listar_usuarios(Cidadao), key=lambda c: c.total_kg_entregue(), reverse=True)

        linhas = [
            "=" * 58,
            "   RELATÓRIO AMBIENTAL - ECOPONTO",
            "=" * 58,
            f"Cidadãos cadastrados .......... {len(self.listar_usuarios(Cidadao))}",
            f"Entregas realizadas ........... {len(self._entregas)}",
            f"Material descartado certo ..... {total_kg:.2f} kg",
        ]
        for destino, kg in kg_por_destino.most_common():
            linhas.append(f"   - {destino.value}: {kg:.2f} kg")
        linhas.append("Por categoria: " + (", ".join(f"{c} {kg:.2f} kg" for c, kg in kg_por_categoria.most_common()) or "-"))
        linhas += [
            f"Pontos emitidos / resgatados .. {pontos_emitidos} / {pontos_gastos}",
            f"Resgates realizados ........... {len(self._resgates)}",
            "-" * 58,
            "Ranking de cidadãos (kg entregues):",
        ]
        for i, c in enumerate(ranking[:5], 1):
            linhas.append(f"   {i}. {c.nome} - {c.total_kg_entregue():.2f} kg - nível {c.nivel()}")
        linhas.append("=" * 58)
        return "\n".join(linhas)
