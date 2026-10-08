import io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

def processar_pagamento_movel(numero, valor, carteira):
    """Simula o envio do pedido de PIN (STK Push) para M-Pesa ou e-Mola."""
    if len(numero) >= 9 and valor > 0:
        print(f"[API] Pedido de {valor} MT enviado para o {numero} via {carteira}")
        return True
    return False

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/gerar-cv', methods=['POST'])
def gerar_cv():
    # Recolha de dados textuais
    nome = request.form.get('nome')
    telefone_cliente = request.form.get('telefone')
    carteira = request.form.get('carteira')
    experiencia = request.form.get('experiencia')
    educacao = request.form.get('educacao')
    
    # Opções visuais do utilizador
    template_escolhido = request.form.get('template', 'classico')
    cor_hex = request.form.get('cor', '#1a365d') # Cor primária seleccionada
    
    # Processamento opcional da fotografia
    foto_file = request.files.get('foto')
    foto_img = None
    if foto_file and foto_file.filename != '':
        try:
            # Lemos a imagem para a memória e convertemos num objecto ReportLab Image
            foto_data = io.BytesIO(foto_file.read())
            # Redimensionamos para um tamanho padrão de foto de passe (ex: 80x100 pontos)
            foto_img = Image(foto_data, width=80, height=100)
        except Exception as e:
            print(f"[Aviso] Falha ao processar fotografia: {e}")
            foto_img = None

    preco_cv = 50 

    # Validação fictícia do pagamento
    sucesso_pagamento = processar_pagamento_movel(telefone_cliente, preco_cv, carteira)
    if not sucesso_pagamento:
        return "Falha no pagamento. Certifique-se de que aceitou o pedido de PIN no telemóvel.", 400

    # Inicialização do PDF em memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    # Definição dos estilos com base na cor escolhida
    cor_principal = colors.HexColor(cor_hex)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=24, textColor=cor_principal, spaceAfter=5)
    section_style = ParagraphStyle('Seccao', parent=styles['Heading2'], fontSize=13, textColor=cor_principal, spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle('Corpo', parent=styles['BodyText'], fontSize=10, leading=14, textColor=colors.HexColor('#333333'))

    elementos = []

    # Bloco de Informação Básica
    bloco_nome = [
        Paragraph(nome.upper(), title_style),
        Paragraph(f"<b>Contacto:</b> {telefone_cliente}", body_style)
    ]

    # --- RENDERIZAÇÃO DOS TEMPLATES ---
    
    if template_escolhido == 'moderno':
        # Layout Moderno: Tabela de duas colunas (Esquerda: Dados/Foto, Direita: Percurso)
        col_esquerda = []
        if foto_img:
            col_esquerda.append(foto_img)
            col_esquerda.append(Spacer(1, 10))
        col_esquerda.extend(bloco_nome)
        
        col_direita = [
            Paragraph("Experiência Profissional", section_style),
            Paragraph(experiencia.replace('\n', '<br/>'), body_style),
            Spacer(1, 10),
            Paragraph("Educação / Formação", section_style),
            Paragraph(educacao.replace('\n', '<br/>'), body_style)
        ]
        
        # Criação da tabela com largura proporcional das colunas (total ~530 pontos)
        tabela_layout = Table([[col_esquerda, col_direita]], colWidths=[180, 350])
        tabela_layout.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('RIGHTPADDING', (0,0), (0,0), 15),
            ('LEFTPADDING', (1,0), (1,0), 15),
            ('LINEAFTER', (0,0), (0,0), 1, cor_principal), # Linha vertical divisória
        ]))
        elementos.append(tabela_layout)

    elif template_escolhido == 'minimalista':
        # Layout Minimalista: Sem linhas, focado em tipografia limpa e espaçamentos
        if foto_img:
            # Alinha foto e nome lado a lado no topo de forma subtil
            tabela_topo = Table([[bloco_nome, foto_img]], colWidths=[430, 100])
            tabela_topo.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
            elementos.append(tabela_topo)
        else:
            elementos.extend(bloco_nome)
            
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("EXPERIÊNCIA PROFISSIONAL", section_style))
        elementos.append(Paragraph(experiencia.replace('\n', '<br/>'), body_style))
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph("EDUCAÇÃO E FORMAÇÃO", section_style))
        elementos.append(Paragraph(educacao.replace('\n', '<br/>'), body_style))

    else: # 'classico'
        # Layout Clássico: Cabeçalho centrado ou tradicional com foto à direita
        if foto_img:
            tabela_cabecalho = Table([[bloco_nome, foto_img]], colWidths=[430, 100])
            tabela_cabecalho.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
            elementos.append(tabela_cabecalho)
        else:
            elementos.extend(bloco_nome)
            
        elementos.append(Spacer(1, 10))
        
        # Adiciona uma barra horizontal decorativa com a cor seleccionada
        tabela_linha = Table([['']], colWidths=[530], rowHeights=[2])
        tabela_linha.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), cor_principal)]))
        elementos.append(tabela_linha)
        elementos.append(Spacer(1, 10))
        
        elementos.append(Paragraph("Experiência Profissional", section_style))
        elementos.append(Paragraph(experiencia.replace('\n', '<br/>'), body_style))
        elementos.append(Spacer(1, 10))
        
        elementos.append(Paragraph("Educação / Formação", section_style))
        elementos.append(Paragraph(educacao.replace('\n', '<br/>'), body_style))

    # Construção do documento PDF
    doc.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CV_{nome.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
