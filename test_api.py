#!/usr/bin/env python3
"""
Teste simples da API de impressão
"""

import requests
import json

def test_print_api():
    # Configurações
    api_base = "http://127.0.0.1:8000"
    api_key = "6b21hrcP1ZjH8yMYD1mqLK74iEjSoDKV"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("=== Teste da API de Impressao ===")
    
    try:
        # Testar endpoint de teste (precisa de token JWT)
        print("1. Testando endpoint de teste...")
        
        # Vamos testar com um token fictício só para ver se o erro 500 foi resolvido
        headers["Authorization"] = "Bearer fake-token-for-test"
        
        test_response = requests.post(
            f"{api_base}/print/test-label",
            headers=headers
        )
        
        print(f"Status: {test_response.status_code}")
        
        if test_response.status_code == 200:
            print("OK: Endpoint de teste funcionando!")
            print("Resposta:", json.dumps(test_response.json(), indent=2))
        else:
            print("ERRO no endpoint de teste:")
            print("Resposta:", test_response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERRO: Nao foi possivel conectar ao servidor")
        print("Certifique-se de que o servidor esta rodando")
    except Exception as e:
        print(f"ERRO inesperado: {e}")

if __name__ == "__main__":
    test_print_api()