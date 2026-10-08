import io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Circle

app = Flask(__name__)

def processar_pagamento_movel(numero, valor, carteira):
    """Simula a validação imediata do pagamento."""
    if len(numero) >= 9 and valor > 0:
        return True
    return False

def desenhar_pontos_nivel(nivel, cor_activa):
    """Gera graficamente 5 bolinhas de nível para as competências."""
    d = Drawing(60, 10)
    cor_inactiva = colors.HexColor('#e2e8f0')
    for i in range(5):
        cor = cor_activa if i < nivel else cor_inactiva
        d.add(Circle(5 + (i * 12), 5, 4, fillColor=cor, strokeColor=None))
    return d

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/gerar-cv', methods=['POST'])
def gerar_cv():
    # Recolha de dados alargada para corresponder ao modelo visual
    nome = request.form.get('nome', '')
    titulo_prof = request.form.get('titulo_profissional', '')
    telefone = request.form.get('telefone', '')
    email = request.form.get('email', '')
    perfil = request.form.get('perfil', '')
    experiencia = request.form.get('experiencia', '')
    educacao = request.form.get('educacao', '')
    
    # Processamento das competências por linhas (Formato: Nome,Nivel de 1 a 5)
    competencias_raw = request.form.get('competencias', '')
    lista_competencias = []
    for linha in competencias_raw.split('\n'):
        if ',' in linha:
            comp, nv = linha.split(',', 1)
            try:
                lista_competencias.append((comp.strip(), min(5, max(1, int(nv.strip())))))
            except:
                pass

    cor_hex = request.form.get('cor', '#1a365d')
    cor_principal = colors.HexColor(cor_hex)
    cor_fundo_lateral = colors.HexColor('#fcfaf7') # Tom suave para a barra lateral

    # Tratamento da imagem
    foto_file = request.files.get('foto')
    foto_img = None
    if foto_file and foto_file.filename != '':
        try:
            foto_data = io.BytesIO(foto_file.read())
            foto_img = Image(foto_data, width=90, height=90)
        except:
            foto_img = None

    # Configuração do documento sem margens internas para colagem perfeita da tabela
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('NomeTop', parent=styles['Heading1'], fontSize=24, textColor=cor_principal, spaceAfter=2)
    subtitle_style = ParagraphStyle('SubTop', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#4a5568'), fontName='Helvetica-Bold', spaceAfter=15)
    
    side_header = ParagraphStyle('SideH', parent=styles['Normal'], fontSize=11, textColor=cor_principal, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
    side_body = ParagraphStyle('SideB', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#2d3748'))
    
    main_header = ParagraphStyle('MainH', parent=styles['Heading2'], fontSize=12, textColor=cor_principal, spaceBefore=14, spaceAfter=6)
    main_body = ParagraphStyle('MainB', parent=styles['BodyText'], fontSize=9.5, leading=14, textColor=colors.HexColor('#333333'))

    # --- MONTAGEM DA BARRA LATERAL (COLUNA ESQUERDA) ---
    elementos_esquerda = []
    if foto_img:
        elementos_esquerda.append(foto_img)
        elementos_esquerda.append(Spacer(1, 15))
    
    elementos_esquerda.append(Paragraph("DADOS PESSOAIS", side_header))
    elementos_esquerda.append(Paragraph(f"<b>Email:</b><br/>{email}", side_body))
    elementos_esquerda.append(Spacer(1, 4))
    elementos_esquerda.append(Paragraph(f"<b>Telefone:</b><br/>{telefone}", side_body))
    
    if lista_competencias:
        elementos_esquerda.append(Spacer(1, 10))
        elementos_esquerda.append(Paragraph("COMPETÊNCIAS", side_header))
        tabela_comp_dados = []
        for comp, nv in lista_competencias:
            tabela_comp_dados.append([Paragraph(comp, side_body), desenhar_pontos_nivel(nv, cor_principal)])
        
        tabela_comp = Table(tabela_comp_dados, colWidths=[90, 65])
        tabela_comp.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elementos_esquerda.append(tabela_comp)

    # --- MONTAGEM DA ÁREA PRINCIPAL (COLUNA DIREITA) ---
    elementos_direita = []
    elementos_direita.append(Paragraph(nome.upper(), title_style))
    elementos_direita.append(Paragraph(titulo_prof.upper(), subtitle_style))
    
    if perfil:
        elementos_direita.append(Paragraph("PERFIL", main_header))
        elementos_direita.append(Paragraph(perfil.replace('\n', '<br/>'), main_body))
    
    elementos_direita.append(Paragraph("EXPERIÊNCIA PROFISSIONAL", main_header))
    elementos_direita.append(Paragraph(experiencia.replace('\n', '<br/>'), main_body))
    
    elementos_direita.append(Paragraph("EDUCAÇÃO E FORMAÇÃO", main_header))
    elementos_direita.append(Paragraph(educacao.replace('\n', '<br/>'), main_body))

    # --- MATRIZ GERAL DO LAYOUT ---
    # Total de largura utilizável é de cerca de 550 pontos (170 esquerda, 380 direita)
    tabela_mestre = Table([[elementos_esquerda, elementos_direita]], colWidths=[175, 375])
    tabela_mestre.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), cor_fundo_lateral),
        ('RIGHTPADDING', (0,0), (0,0), 12),
        ('LEFTPADDING', (0,0), (0,0), 12),
        ('LEFTPADDING', (1,0), (1,0), 18),
        ('LINEAFTER', (0,0), (0,0), 1.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story = [tabela_mestre]
    doc.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CV_{nome.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)


