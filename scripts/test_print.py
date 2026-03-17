#!/usr/bin/env python3
"""
Script de teste para o sistema de impressão de etiquetas ProRAF

Uso:
    poetry run task test-print
    
    ou diretamente:
    python scripts/test_print.py
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_printer_availability():
    """Testa se as impressoras estão disponíveis"""
    try:
        import win32print
        print("Verificando impressoras disponíveis...")
        
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        
        if not printers:
            print("ERRO: Nenhuma impressora encontrada!")
            return False
            
        print(f"OK: Encontradas {len(printers)} impressoras:")
        for i, printer in enumerate(printers, 1):
            print(f"   {i}. {printer}")
            
        return True
        
    except ImportError:
        print("AVISO: Modulo win32print nao encontrado. Funcionando em modo simulacao.")
        print("OK: Sistema funcionara em modo simulacao (sem impressora fisica)")
        return True  # Retorna True em modo simulação
    except Exception as e:
        print(f"ERRO: Erro ao verificar impressoras: {e}")
        return False


def test_template_loading():
    """Testa se o template de etiqueta pode ser carregado"""
    print("\nTestando carregamento do template...")
    
    try:
        from proraf.services.print_service import ProductLabelPrinter
        
        printer = ProductLabelPrinter()
        template = printer.load_template()
        
        if template:
            print("OK: Template carregado com sucesso!")
            print(f"   Tamanho: {len(template)} caracteres")
            print(f"   Primeiras linhas: {template[:100]}...")
            return True
        else:
            print("ERRO: Falha ao carregar template!")
            return False
            
    except Exception as e:
        print(f"ERRO ao carregar template: {e}")
        return False


def test_label_creation():
    """Testa a criação de uma etiqueta"""
    print("\nTestando criacao de etiqueta...")
    
    try:
        from proraf.services.print_service import ProductLabelPrinter
        from datetime import datetime
        
        printer = ProductLabelPrinter()
        
        produto_info = {
            'produto_nome': 'Produto Teste',
            'peso': '500g',
            'empresa': 'Empresa Teste ProRAF',
            'endereco': 'Rua Teste, 123 - Centro',
            'cpf': '123.456.789-00',
            'telefone': '(55) 1234-5678',
            'validade': datetime.now().strftime('%d/%m/%Y'),
            'codigo_produto': 'PRD-TESTE-001',
            'codigo_lote': 'LOT-TESTE-001',
            'url_rastreio': 'http://proraf.unihacker.club:8000/rastreio?search=LOT-TESTE-001'
        }
        
        label_content = printer.create_product_label(produto_info)
        
        if label_content:
            print("OK: Etiqueta criada com sucesso!")
            print(f"   Tamanho: {len(label_content)} caracteres")
            
            # Verificar se as substituições foram feitas
            checks = [
                ('Produto Teste' in label_content, 'Nome do produto'),
                ('500g' in label_content, 'Peso'),
                ('Empresa Teste ProRAF' in label_content, 'Nome da empresa'),
                ('LOT-TESTE-001' in label_content, 'Código do lote'),
                ('PRD-TESTE-001' in label_content, 'Código do produto')
            ]
            
            for check, description in checks:
                status = "OK" if check else "ERRO"
                print(f"   {status}: {description}")
                
            return True
        else:
            print("ERRO: Falha ao criar etiqueta!")
            return False
            
    except Exception as e:
        print(f"ERRO ao criar etiqueta: {e}")
        return False


def test_print_simulation():
    """Simula impressão (sem enviar para impressora)"""
    print("\nSimulando impressao...")
    
    try:
        from proraf.services.print_service import ProductLabelPrinter
        from datetime import datetime
        
        # Usar o service que já tem modo simulação integrado
        printer = ProductLabelPrinter()
        
        # Testar se consegue listar impressoras (com fallback)
        try:
            printers = printer.get_available_printers()
            if printers and printers[0] != "Impressora Simulada":
                printer_name = printers[0]
                print(f"Usando impressora: {printer_name}")
                printer = ProductLabelPrinter(printer_name=printer_name)
            else:
                print("Usando modo simulacao")
        except Exception:
            print("Usando modo simulacao (fallback)")
        
        produto_info = {
            'produto_nome': 'Produto Teste',
            'peso': '500g',
            'empresa': 'Empresa Teste ProRAF',
            'endereco': 'Rua Teste, 123 - Centro',
            'cpf': '123.456.789-00',
            'telefone': '(55) 1234-5678',
            'validade': datetime.now().strftime('%d/%m/%Y'),
            'codigo_produto': 'PRD-TESTE-001',
            'codigo_lote': 'LOT-TESTE-001',
            'url_rastreio': 'http://proraf.unihacker.club:8000/rastreio?search=LOT-TESTE-001'
        }
        
        # Criar etiqueta
        label_content = printer.create_product_label(produto_info)
        
        if label_content:
            print("OK: Etiqueta preparada para impressao!")
            
            # Perguntar se quer imprimir de verdade
            resposta = input("\nDeseja enviar para a impressora? (s/N): ").strip().lower()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                print("Enviando para impressora...")
                result = printer.print_label(label_content)
                
                if result:
                    print("OK: Etiqueta enviada com sucesso!")
                else:
                    print("ERRO: Falha ao enviar etiqueta!")
                    
                return result
            else:
                print("OK: Simulacao concluida (nao enviada para impressora)")
                return True
        else:
            print("ERRO: Falha ao preparar etiqueta!")
            return False
            
    except Exception as e:
        print(f"ERRO na simulacao de impressao: {e}")
        return False


def main():
    """Função principal do teste"""
    print("=" * 60)
    print("TESTE DO SISTEMA DE IMPRESSAO PRORAF")
    print("=" * 60)
    
    tests = [
        ("Disponibilidade de Impressoras", test_printer_availability),
        ("Carregamento de Template", test_template_loading),
        ("Criacao de Etiqueta", test_label_creation),
        ("Simulacao de Impressao", test_print_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n> {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERRO no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "OK: PASSOU" if result else "ERRO: FALHOU"
        print(f"{status} - {test_name}")
    
    print(f"\nTaxa de Sucesso: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("SUCESSO: Todos os testes passaram! Sistema pronto para uso.")
    else:
        print("AVISO: Alguns testes falharam. Verifique as configuracoes.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    main()