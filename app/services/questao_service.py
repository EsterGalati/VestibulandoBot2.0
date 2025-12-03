from app.models.questao import QuestaoENEM
from app.models.questao_alternativa import QuestaoAlternativa
from app.services.enem_api_service import EnemAPIService
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any
import time

MATERIA_MAP = {
    "linguagens": 1,
    "matematica": 4,
    "natureza": 3,
    "ciencias-natureza": 3,
    "humanas": 2,
    "ciencias-humanas": 2,
}

class QuestaoService:
    """Serviço para manipular questões de professores e questões ENEM."""

    @staticmethod
    def listar_todas():
        questoes = QuestaoENEM.query.all()
        return QuestaoService._formatar_lista(questoes)

    @staticmethod
    def listar_por_materia(cod_materia: int):
        """
        Importa ENEM (somente 1x) e depois lista por matéria.
        Separado em: professor e ENEM.
        """

        questoes = QuestaoENEM.query.filter_by(cod_materia=cod_materia).all()

        professor = []
        enem = []

        for q in questoes:
            bloco = {
                "cod_questao": q.cod_questao,
                "tx_questao": q.tx_questao,
                "ano_questao": q.ano_questao,
                "cod_materia": q.cod_materia,
                "tx_resposta_correta": q.tx_resposta_correta,
                "tx_imagem_url": q.tx_imagem_url,
                "alternativas": [
                    {
                        "cod_alternativa": alt.cod_alternativa,
                        "tx_letra": alt.tx_letra,
                        "tx_texto": alt.tx_texto
                    }
                    for alt in q.alternativas
                ]
            }

            origem = q.origem.upper() if q.origem else "PROFESSOR"
            if origem == "ENEM":
                enem.append(bloco)
            else:
                professor.append(bloco)

        return {
            "professor": professor,
            "enem": enem
        }

    @staticmethod
    def _formatar_lista(questoes):
        resultado = []
        for q in questoes:
            resultado.append({
                "cod_questao": q.cod_questao,
                "tx_questao": q.tx_questao,
                "cod_materia": q.cod_materia,
                "ano_questao": q.ano_questao,
                "tx_resposta_correta": q.tx_resposta_correta,
                "origem": q.origem,
                "tx_imagem_url": q.tx_imagem_url,
                "alternativas": [
                    {
                        "cod_alternativa": alt.cod_alternativa,
                        "tx_letra": alt.tx_letra,
                        "tx_texto": alt.tx_texto
                    }
                    for alt in q.alternativas
                ]
            })
        return resultado

    @staticmethod
    def buscar_por_id(cod_questao: int):
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None

        return {
            "cod_questao": questao.cod_questao,
            "tx_questao": questao.tx_questao,
            "cod_materia": questao.cod_materia,
            "ano_questao": questao.ano_questao,
            "tx_resposta_correta": questao.tx_resposta_correta,
            "tx_imagem_url": questao.tx_imagem_url,
            "alternativas": [
                {
                    "cod_alternativa": a.cod_alternativa,
                    "tx_letra": a.tx_letra,
                    "tx_texto": a.tx_texto
                }
                for a in questao.alternativas
            ]
        }

    @staticmethod
    def criar(dados: dict):
        q = QuestaoENEM(
            tx_questao=dados["tx_questao"].strip(),
            cod_materia=int(dados["cod_materia"]),
            ano_questao=int(dados["ano_questao"]),
            tx_resposta_correta=dados["tx_resposta_correta"].upper().strip(),
            tx_bncc=dados.get("bncc") or dados.get("tx_bncc"),
            origem="PROFESSOR",
            tx_imagem_url=None
        )
        db.session.add(q)
        db.session.flush()

        for alt in dados.get("alternativas", []):
            db.session.add(
                QuestaoAlternativa(
                    cod_questao=q.cod_questao,
                    tx_letra=alt["tx_letra"].upper(),
                    tx_texto=alt["tx_texto"].strip(),
                )
            )

        db.session.commit()
        return {"cod_questao": q.cod_questao}

    @staticmethod
    def atualizar(cod_questao: int, dados: dict):
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None

        questao.tx_questao = dados.get("tx_questao", questao.tx_questao)
        questao.cod_materia = int(dados.get("cod_materia", questao.cod_materia))
        questao.ano_questao = int(dados.get("ano_questao", questao.ano_questao))
        questao.tx_resposta_correta = dados.get(
            "tx_resposta_correta", questao.tx_resposta_correta
        ).upper()
        questao.bncc = dados.get("bncc", questao.bncc)

        if "alternativas" in dados:
            QuestaoAlternativa.query.filter_by(cod_questao=questao.cod_questao).delete()

            for alt in dados["alternativas"]:
                db.session.add(
                    QuestaoAlternativa(
                        cod_questao=questao.cod_questao,
                        tx_letra=alt["tx_letra"].upper(),
                        tx_texto=alt["tx_texto"].strip(),
                    )
                )

        db.session.commit()
        return {"cod_questao": questao.cod_questao}

    @staticmethod
    def deletar(cod_questao: int):
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None

        QuestaoAlternativa.query.filter_by(cod_questao=cod_questao).delete()
        db.session.delete(questao)
        db.session.commit()
        return {"mensagem": f"Questão {cod_questao} removida com sucesso."}

    @staticmethod
    def importar_enem(ano: int, codigos_materias_filtro: List[int]) -> Dict[str, Any]:
        print(f"DEBUG: INICIANDO IMPORTAÇÃO ENEM {ano} para matérias: {codigos_materias_filtro}")
        
        questoes_importadas = 0
        questoes_duplicadas = 0
        erros = []

        try:
            questoes_api = EnemAPIService.listar_questoes_por_ano(ano)
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao buscar questões na API do ENEM: {str(e)}"}

        codigos_materias = codigos_materias_filtro # Usar a lista de matérias fornecida
        
        # Mapeamento reverso para filtrar as questões da API
        mapa_reverso_materia = {v: k for k, v in MATERIA_MAP.items()}
        areas_enem_permitidas = [mapa_reverso_materia[cod] for cod in codigos_materias if cod in mapa_reverso_materia]
        
        questoes_filtradas = [
            q_api for q_api in questoes_api 
            if q_api.get("discipline") in areas_enem_permitidas
        ]
        
        total_questoes_filtradas = len(questoes_filtradas)
        
        # Lógica de balanceamento de questões (mantida, mas adaptada ao filtro)
        minimo_por_materia = (total_questoes_filtradas // len(codigos_materias)) if total_questoes_filtradas > 0 else 0
        contagem_por_materia = {cod: 0 for cod in codigos_materias}
        questoes_excedentes = []

        for q_api in questoes_filtradas:
            titulo_enem = q_api.get("title", "Questão sem título")

            try:
                area = q_api.get("discipline")
                cod_materia = MATERIA_MAP.get(area)

                if not cod_materia or cod_materia not in codigos_materias_filtro:
                    # Esta verificação é redundante devido ao filtro inicial, mas mantida por segurança
                    erros.append(f"Questão '{titulo_enem}' ignorada: Área '{area}' não mapeada ou não solicitada. cod_materia={cod_materia}")
                    continue

                if contagem_por_materia[cod_materia] >= minimo_por_materia:
                    questoes_excedentes.append(q_api)
                    continue

                enunciado = q_api.get("context")
                if not enunciado:
                    erros.append(f"Questão '{titulo_enem}' ignorada: Enunciado (context) é nulo.")
                    continue
                
                if QuestaoENEM.query.filter_by(ano_questao=ano, tx_questao=enunciado).first():
                    questoes_duplicadas += 1
                    continue

                tx_imagem_url = None
                files = q_api.get("files")
                if files and isinstance(files, list) and len(files) > 0:
                    first_file = files[0]
                    if isinstance(first_file, dict):
                        tx_imagem_url = first_file.get("url")
                
                nova_questao = QuestaoENEM(
                    tx_questao=enunciado,
                    ano_questao=ano,
                    tx_resposta_correta=q_api.get("correctAlternative"),
                    cod_materia=cod_materia,
                    origem="ENEM",
                    tx_imagem_url=tx_imagem_url
                )
                db.session.add(nova_questao)

                alternativas_api = q_api.get("alternatives", [])
                print(f"DEBUG: Criando {len(alternativas_api)} alternativas...")
                
                for alt_api in alternativas_api:
                    nova_alternativa = QuestaoAlternativa(
                        questao=nova_questao,
                        tx_letra=alt_api.get("letter"),
                        tx_texto=alt_api.get("text")
                    )
                    db.session.add(nova_alternativa)

                questoes_importadas += 1
                contagem_por_materia[cod_materia] += 1
                
            except SQLAlchemyError as e:
                db.session.rollback()
            except Exception as e:
                db.session.rollback()
        
        for q_api in questoes_excedentes:
            titulo_enem = q_api.get("title", "Questão sem título")
            area = q_api.get("discipline")
            cod_materia = MATERIA_MAP.get(area)
            
            # Garantir que a matéria excedente é uma das solicitadas
            if cod_materia in codigos_materias_filtro and contagem_por_materia.get(cod_materia, 0) < minimo_por_materia:
                try:
                    enunciado = q_api.get("context")
                    if not enunciado:
                        continue
                    
                    tx_imagem_url = None
                    files = q_api.get("files")
                    if files and isinstance(files, list) and len(files) > 0:
                        first_file = files[0]
                        if isinstance(first_file, dict):
                            tx_imagem_url = first_file.get("url")

                    nova_questao = QuestaoENEM(
                        tx_questao=enunciado,
                        ano_questao=ano,
                        tx_resposta_correta=q_api.get("correctAlternative"),
                        cod_materia=cod_materia,
                        origem="ENEM",
                        tx_imagem_url=tx_imagem_url
                    )
                    db.session.add(nova_questao)

                    for alt_api in q_api.get("alternatives", []):
                        nova_alternativa = QuestaoAlternativa(
                            questao=nova_questao,
                            tx_letra=alt_api.get("letter"),
                            tx_texto=alt_api.get("text")
                        )
                        db.session.add(nova_alternativa)

                    questoes_importadas += 1
                    contagem_por_materia[cod_materia] += 1

                except SQLAlchemyError as e:
                    db.session.rollback()
                except Exception as e:
                    db.session.rollback()

        print(f"\nDEBUG: Contagem final Questões: {questoes_importadas}")
        print(f"DEBUG: Contagem final por matéria: {contagem_por_materia}")
        
        try:
            db.session.commit()
            return {
                "status": "sucesso",
                "ano": ano,
                "importadas": questoes_importadas,
                "duplicadas_ignoradas": questoes_duplicadas,
                "erros": erros,
                "mensagem": f"{questoes_importadas} questões do ENEM {ano} importadas com sucesso. {questoes_duplicadas} duplicadas ignoradas."
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "erro", "mensagem": f"Erro ao finalizar a transação de importação: {str(e)}"}
        except Exception as e:
            db.session.rollback()
            return {"status": "erro", "mensagem": f"Erro inesperado ao finalizar a importação: {str(e)}"}
