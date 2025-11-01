try:
    import win32print
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("AVISO: win32print nao disponivel. Sistema funcionara em modo simulacao.")

import csv
import re
import time
import os
from datetime import datetime, timedelta
from pathlib import Path


class ProductLabelPrinter:
    def __init__(self, printer_name="ZDesigner ZT230-200dpi ZPL"):
        self.printer_name = printer_name
        self.template_file = "static/templates/etiquetaExemplo.prn"
        
    def load_template(self):
        """Carrega o template da etiqueta do arquivo PRN"""
        try:
            # Tentar diferentes caminhos para o template
            possible_paths = [
                self.template_file,
                os.path.join(os.getcwd(), self.template_file),
                os.path.join(Path(__file__).parent.parent.parent, self.template_file)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as file:
                        return file.read()
            
            print(f"Arquivo de template não encontrado em nenhum dos caminhos: {possible_paths}")
            return None
        except Exception as e:
            print(f"Erro ao carregar template: {e}")
            return None
    
    def create_product_label(self, produto_info):
        """
        Cria uma etiqueta substituindo as informações no template
        
        produto_info deve ser um dicionário com as chaves:
        - produto_nome: Nome do produto (ex: "Laranja")
        - peso: Peso do produto (ex: "500g")
        - empresa: Nome da empresa (ex: "Laranjas da Tati")
        - endereco: Endereço (ex: "Rosa 985- Zona Rural")
        - cpf: CPF (ex: "458.685.878.66")
        - telefone: Telefone (ex: "(55) 3322-5544")
        - validade: Data de validade (ex: "10/10/2025")
        - codigo_produto: Código do produto (ex: "PRD-60920")
        - codigo_lote: Código do lote (ex: "LOT-64208")
        - url_rastreio: URL para rastreamento (opcional)
        """
        template = self.load_template()
        if template is None:
            return None
        
        # Dicionário de substituições com valores padrão
        defaults = {
            'produto_nome': 'Produto',
            'peso': '500g',
            'empresa': 'Empresa',
            'endereco': 'Endereço',
            'cpf': '000.000.000-00',
            'telefone': '(00) 0000-0000',
            'validade': datetime.now().strftime('%d/%m/%Y'),
            'codigo_produto': 'PRD-00000',
            'codigo_lote': 'LOT-00000',
            'url_rastreio': 'http://proraf.unihacker.club:8000/rastreio?search={codigo_lote}'
        }
        
        # Mescla valores padrão com valores fornecidos
        info = {**defaults, **produto_info}
        
        # URL de rastreamento com código do lote
        if '{codigo_lote}' in info['url_rastreio']:
            info['url_rastreio'] = info['url_rastreio'].format(codigo_lote=info['codigo_lote'])
        
        # Método mais seguro: substituir strings diretamente sem regex complexo
        new_label = template
        
        # Substituições específicas usando replace (mais seguro que regex)
        # Nome do produto (Laranja -> novo nome)
        new_label = new_label.replace('^FDLaranja^FS', '^FD{}^FS'.format(info['produto_nome']))
        
        # Peso líquido
        new_label = new_label.replace('Peso líquido (500g)', 'Peso líquido ({})'.format(info['peso']))
        
        # Nome da empresa
        new_label = new_label.replace('^FDLaranjas da Tati^FS', '^FD{}^FS'.format(info['empresa']))
        
        # Endereço
        new_label = new_label.replace('^FDRosa 985- Zona Rural^FS', '^FD{}^FS'.format(info['endereco']))
        
        # CPF
        new_label = new_label.replace('CPF: 458.685.878.66', 'CPF: {}'.format(info['cpf']))
        
        # Telefone
        new_label = new_label.replace('Tel: (55) 3322-5544', 'Tel: {}'.format(info['telefone']))
        
        # Validade
        new_label = new_label.replace('Val: 10/10/2025', 'Val: {}'.format(info['validade']))
        
        # Código do produto
        new_label = new_label.replace('Código Produto: PRD-60920', 'Código Produto: {}'.format(info['codigo_produto']))
        
        # Código do lote
        new_label = new_label.replace('Código Lote: LOT-64208', 'Código Lote: {}'.format(info['codigo_lote']))
        
        # URL do QR Code
        new_label = new_label.replace('http://proraf.unihacker.club:8000/rastreio?search=LOT-64208', info['url_rastreio'])
        
        return new_label
    
    def print_label(self, zpl_content):
        """Envia o conteúdo ZPL para a impressora"""
        if not WIN32_AVAILABLE:
            print("Modo simulacao - Etiqueta seria enviada para:", self.printer_name)
            print("Conteudo ZPL preparado:", len(zpl_content), "caracteres")
            return True  # Simula sucesso
            
        try:
            printer_handle = win32print.OpenPrinter(self.printer_name)
            job_info = ("Etiqueta Produto", None, "RAW")
            job_id = win32print.StartDocPrinter(printer_handle, 1, job_info)
            win32print.StartPagePrinter(printer_handle)
            win32print.WritePrinter(printer_handle, zpl_content.encode('utf-8'))
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)
            return True
        except Exception as e:
            print(f"Erro ao imprimir: {e}")
            return False
    
    def print_product_label(self, produto_info):
        """Imprime uma etiqueta de produto"""
        print(f"Preparando etiqueta para produto: {produto_info.get('produto_nome', 'Produto')}")
        
        label_content = self.create_product_label(produto_info)
        if label_content:
            success = self.print_label(label_content)
            if success:
                print(f"Etiqueta do produto '{produto_info.get('produto_nome', 'Produto')}' impressa com sucesso!")
            return success
        else:
            print("Erro ao criar a etiqueta")
            return False
    
    def get_available_printers(self):
        """Retorna lista de impressoras disponíveis"""
        if not WIN32_AVAILABLE:
            return ["Impressora Simulada"]
            
        try:
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            return printers
        except Exception as e:
            print(f"Erro ao listar impressoras: {e}")
            return []

    def read_products_csv(self, csv_file="produtos.csv"):
        """Lê produtos do arquivo CSV"""
        products = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Remove espaços em branco dos valores
                    product = {k: v.strip() if v else '' for k, v in row.items()}
                    if product.get('produto_nome'):  # Só adiciona se tiver nome do produto
                        products.append(product)
            return products
        except FileNotFoundError:
            print(f"Arquivo {csv_file} não encontrado!")
            return []
        except Exception as e:
            print(f"Erro ao ler arquivo CSV: {e}")
            return []
    
    def print_from_csv(self, csv_file="produtos.csv", delay_seconds=3):
        """Imprime etiquetas para todos os produtos do arquivo CSV"""
        products = self.read_products_csv(csv_file)
        
        if not products:
            print("Nenhum produto encontrado no arquivo CSV!")
            return False
        
        print(f"\nEncontrados {len(products)} produtos no arquivo CSV")
        print("Produtos a serem impressos:")
        for i, produto in enumerate(products, 1):
            print(f"  {i:2d}. {produto.get('produto_nome', 'N/A')} - Lote: {produto.get('codigo_lote', 'N/A')}")
        
        resposta = input(f"\nDeseja imprimir {len(products)} etiquetas? (s/n): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("Impressão cancelada.")
            return False
        
        sucessos = 0
        falhas = 0
        
        print(f"\nIniciando impressão com intervalo de {delay_seconds} segundos...")
        print("=" * 70)
        
        for i, produto in enumerate(products, 1):
            print(f"Processando {i:2d}/{len(products)}: {produto.get('produto_nome', 'Produto')}")
            
            if self.print_product_label(produto):
                sucessos += 1
                print(f"✓ Sucesso!")
            else:
                falhas += 1
                print(f"✗ Falha!")
            
            if i < len(products):
                print(f"Aguardando {delay_seconds} segundos...")
                time.sleep(delay_seconds)
            
            print("-" * 70)
        
        print(f"\nResumo da impressão:")
        print(f"Total de etiquetas: {len(products)}")
        print(f"Sucessos: {sucessos}")
        print(f"Falhas: {falhas}")
        print(f"Taxa de sucesso: {(sucessos/len(products)*100):.1f}%")
        
        return sucessos > 0
