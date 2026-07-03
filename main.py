# -*- coding: utf-8 -*-
"""
Extrator de Desenhos LS Control — aplicativo desktop Windows.

Fluxo: selecionar pasta raiz -> escanear PDFs -> revisar/editar na tabela -> exportar
para a planilha OS ACOMPANHAMENTO (.xlsm) existente.
"""
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QComboBox, QProgressBar, QPlainTextEdit, QCheckBox, QMessageBox,
    QHeaderView, QAbstractItemView,
)

from extrator import escanear_pasta, gerar_linhas

PROCESSOS = ["", "CNC", "USINAGEM", "ESTRUTURA E CONJ. SOLDADO",
             "CALDEIRARIA", "CORTE ÁGUA", "IMPRESSÃO 3D", "COMPRA"]

COLUNAS = ["✔", "DESENHO", "REV.", "QTDE", "PROCESSO",
           "DESCRIÇÃO", "DIMENSÃO SOLICITADA", "MATERIAL", "QTD", "ARQUIVO"]


class ThreadVarredura(QThread):
    progresso = Signal(int, int, str)
    concluido = Signal(list)
    falhou = Signal(str)

    def __init__(self, pasta: Path):
        super().__init__()
        self.pasta = pasta

    def run(self):
        try:
            resultados = escanear_pasta(
                self.pasta,
                callback=lambda i, n, nome: self.progresso.emit(i, n, nome))
            self.concluido.emit(resultados)
        except Exception:
            self.falhou.emit(traceback.format_exc())


class ThreadExportacao(QThread):
    log = Signal(str)
    concluido = Signal(dict)
    falhou = Signal(str)

    def __init__(self, caminho_xlsm: str, linhas: list):
        super().__init__()
        self.caminho_xlsm = caminho_xlsm
        self.linhas = linhas

    def run(self):
        try:
            from exportador import exportar
            r = exportar(self.caminho_xlsm, self.linhas, log=self.log.emit)
            self.concluido.emit(r)
        except Exception:
            self.falhou.emit(traceback.format_exc())


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extrator de Desenhos — LS Control")
        self.resize(1280, 760)
        self._montar_ui()
        self._thread = None

    # ------------------------------------------------------------------ UI
    def _montar_ui(self):
        central = QWidget()
        raiz = QVBoxLayout(central)

        # pasta raiz
        linha1 = QHBoxLayout()
        linha1.addWidget(QLabel("Pasta raiz dos PDFs:"))
        self.ed_pasta = QLineEdit()
        linha1.addWidget(self.ed_pasta, 1)
        btn_pasta = QPushButton("Procurar…")
        btn_pasta.clicked.connect(self._escolher_pasta)
        linha1.addWidget(btn_pasta)
        self.btn_escanear = QPushButton("Escanear")
        self.btn_escanear.clicked.connect(self._escanear)
        linha1.addWidget(self.btn_escanear)
        raiz.addLayout(linha1)

        # planilha destino
        linha2 = QHBoxLayout()
        linha2.addWidget(QLabel("Planilha destino (.xlsm):"))
        self.ed_planilha = QLineEdit()
        linha2.addWidget(self.ed_planilha, 1)
        btn_plan = QPushButton("Procurar…")
        btn_plan.clicked.connect(self._escolher_planilha)
        linha2.addWidget(btn_plan)
        raiz.addLayout(linha2)

        # progresso
        self.barra = QProgressBar()
        self.barra.setTextVisible(True)
        raiz.addWidget(self.barra)

        # tabela de revisão
        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        raiz.addWidget(self.tabela, 1)

        # rodapé
        linha3 = QHBoxLayout()
        self.chk_todos = QCheckBox("Marcar/desmarcar todos")
        self.chk_todos.setChecked(True)
        self.chk_todos.stateChanged.connect(self._marcar_todos)
        linha3.addWidget(self.chk_todos)
        linha3.addStretch(1)
        self.lbl_resumo = QLabel("")
        linha3.addWidget(self.lbl_resumo)
        self.btn_exportar = QPushButton("Exportar para planilha")
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self._exportar)
        linha3.addWidget(self.btn_exportar)
        raiz.addLayout(linha3)

        # log
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(140)
        raiz.addWidget(self.log)

        self.setCentralWidget(central)

    # ------------------------------------------------------------- helpers
    def _logar(self, msg: str):
        self.log.appendPlainText(msg)

    def _escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta raiz dos PDFs")
        if pasta:
            self.ed_pasta.setText(pasta)

    def _escolher_planilha(self):
        arq, _ = QFileDialog.getOpenFileName(
            self, "Selecione a planilha destino", "",
            "Planilhas Excel com macro (*.xlsm);;Todas (*.*)")
        if arq:
            self.ed_planilha.setText(arq)

    def _marcar_todos(self, estado):
        for r in range(self.tabela.rowCount()):
            w = self.tabela.cellWidget(r, 0)
            if isinstance(w, QCheckBox):
                w.setChecked(estado == Qt.Checked.value or estado == 2)

    # ------------------------------------------------------------ varredura
    def _escanear(self):
        pasta = Path(self.ed_pasta.text().strip().strip('"'))
        if not pasta.is_dir():
            QMessageBox.warning(self, "Atenção", "Selecione uma pasta raiz válida.")
            return
        self.btn_escanear.setEnabled(False)
        self.btn_exportar.setEnabled(False)
        self.tabela.setRowCount(0)
        self.barra.setValue(0)
        self._logar(f"Escaneando: {pasta}")
        self._thread = ThreadVarredura(pasta)
        self._thread.progresso.connect(self._ao_progredir)
        self._thread.concluido.connect(self._ao_concluir_varredura)
        self._thread.falhou.connect(self._ao_falhar)
        self._thread.start()

    def _ao_progredir(self, atual, total, nome):
        self.barra.setMaximum(total)
        self.barra.setValue(atual)
        self.barra.setFormat(f"{atual}/{total} — {nome}")

    def _ao_concluir_varredura(self, resultados):
        self.btn_escanear.setEnabled(True)
        com_erro = [d for d in resultados if d.erro]
        for d in com_erro:
            self._logar(f"⚠ {d.arquivo}: {d.erro}")
        linhas = []
        for d in resultados:
            if not d.erro:
                linhas.extend(gerar_linhas(d))
        self._popular_tabela(linhas)
        self._logar(f"Concluído: {len(resultados)} PDF(s), {len(linhas)} linha(s), "
                    f"{len(com_erro)} com problema.")
        self.btn_exportar.setEnabled(bool(linhas))

    def _ao_falhar(self, erro):
        self.btn_escanear.setEnabled(True)
        self._logar(erro)
        QMessageBox.critical(self, "Erro", "Falha na operação. Veja o log.")

    def _popular_tabela(self, linhas):
        self.tabela.setRowCount(len(linhas))
        for r, ln in enumerate(linhas):
            chk = QCheckBox()
            chk.setChecked(True)
            chk.setStyleSheet("margin-left: 12px;")
            self.tabela.setCellWidget(r, 0, chk)

            valores = [ln["desenho"], ln["rev"], str(ln["qtde"]), None,
                       ln["descricao"], ln["dimensao"], ln["material"],
                       str(ln["qtd"]), ln["arquivo"]]
            for c, v in enumerate(valores, start=1):
                if c == 4:  # PROCESSO -> combo editável
                    combo = QComboBox()
                    combo.setEditable(True)
                    combo.addItems(PROCESSOS)
                    self.tabela.setCellWidget(r, 4, combo)
                    continue
                item = QTableWidgetItem(v or "")
                if c == 9:  # ARQUIVO somente leitura
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabela.setItem(r, c, item)
        self.tabela.resizeColumnsToContents()
        self.lbl_resumo.setText(f"{len(linhas)} linha(s) para revisão")

    # ----------------------------------------------------------- exportação
    def _linhas_marcadas(self):
        linhas = []
        for r in range(self.tabela.rowCount()):
            chk = self.tabela.cellWidget(r, 0)
            if not (isinstance(chk, QCheckBox) and chk.isChecked()):
                continue
            combo = self.tabela.cellWidget(r, 4)
            get = lambda c: (self.tabela.item(r, c).text().strip()
                             if self.tabela.item(r, c) else "")
            linhas.append({
                "desenho": get(1), "rev": get(2), "qtde": get(3),
                "processo": combo.currentText().strip() if combo else "",
                "descricao": get(5), "dimensao": get(6),
                "material": get(7), "qtd": get(8),
            })
        return linhas

    def _exportar(self):
        caminho = self.ed_planilha.text().strip().strip('"')
        if not caminho:
            QMessageBox.warning(self, "Atenção", "Selecione a planilha destino (.xlsm).")
            return
        linhas = self._linhas_marcadas()
        if not linhas:
            QMessageBox.information(self, "Nada a exportar",
                                    "Nenhuma linha marcada para exportação.")
            return
        resp = QMessageBox.question(
            self, "Confirmar exportação",
            f"Inserir {len(linhas)} linha(s) na aba OS ACOMPANHAMENTO?\n"
            f"Um backup da planilha será criado antes.")
        if resp != QMessageBox.Yes:
            return
        self.btn_exportar.setEnabled(False)
        self._thread = ThreadExportacao(caminho, linhas)
        self._thread.log.connect(self._logar)
        self._thread.concluido.connect(self._ao_concluir_exportacao)
        self._thread.falhou.connect(self._ao_falhar_exportacao)
        self._thread.start()

    def _ao_concluir_exportacao(self, r):
        self.btn_exportar.setEnabled(True)
        QMessageBox.information(
            self, "Exportação concluída",
            f"{r['inseridas']} linha(s) inserida(s), {r['puladas']} pulada(s) "
            f"(duplicadas).\nBackup: {r['backup']}")

    def _ao_falhar_exportacao(self, erro):
        self.btn_exportar.setEnabled(True)
        self._logar(erro)
        QMessageBox.critical(
            self, "Erro na exportação",
            "Falha ao gravar na planilha. Verifique se o arquivo não está aberto "
            "no Excel e veja o log para detalhes.")


def main():
    app = QApplication(sys.argv)
    jan = JanelaPrincipal()
    jan.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
