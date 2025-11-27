import requests
import time

class EnemAPIService:
    BASE_URL = "https://api.enem.dev/v1/exams"

    @staticmethod
    def listar_questoes_por_ano(ano: int ):
        
        todas_questoes = []
        offset = 0
        limit = 50
        has_more = True

        while has_more:
            url = f"{EnemAPIService.BASE_URL}/{ano}/questions?limit={limit}&offset={offset}"
            r = requests.get(url, timeout=30)

            if r.status_code != 200:
                raise Exception(f"Erro ao buscar ENEM {ano}: {r.status_code} - {r.text}")

            data = r.json()
            
            todas_questoes.extend(data.get("questions", []))
            
            metadata = data.get("metadata", {})
            has_more = metadata.get("hasMore", False)
            offset += limit
            
            if not has_more:
                break
            
            time.sleep(0.5) 

        return todas_questoes
