import io
import uuid
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

TRANSACCOES = {}
DADOS_CV = {}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/iniciar-pagamento', methods=['POST'])
def iniciar_pagamento():
    telefone = request.form.get('telefone')
    carteira = request.form.get('carteira')
    
    if not telefone or len(telefone) < 9:
        return jsonify({"status": "ERROR", "message": "Número de telefone inválido."}), 400

    ref_id = str(uuid.uuid4())
    
    # Armazenamento seguro de todos os dados preenchidos
    DADOS_CV[ref_id] = {
        "nome": request.form.get('nome', ''),
        "titulo": request.form.get('titulo_profissional', ''),
        "email": request.form.get('email', ''),
        "telefone_contacto": request.form.get('telefone_contacto', ''),
        "perfil": request.form.get('perfil', ''),
        "experiencia": request.form.get('experiencia', ''),
        "educacao": request.form.get('educacao', ''),
        "competencias": request.form.get('competencias', ''),
        "cor": request.form.get('cor', '#1a365d')
    }
    
    TRANSACCOES[ref_id] = "PENDING"
    print(f"[API] Solicitado pagamento de 50 MT ao {telefone} via {carteira}. Ref: {ref_id}")
    
    return jsonify({"status": "SUCCESS", "ref": ref_id})

@app.route('/checar-status/<ref_id>', methods=['GET'])
def checar_status(ref_id):
    status = TRANSACCOES.get(ref_id, "NOT_FOUND")
    return jsonify({"status": status})

@app.route('/simular-sucesso/<ref_id>', methods=['GET'])
def simular_sucesso(ref_id):
    if ref_id in TRANSACCOES:
        TRANSACCOES[ref_id] = "PAID"
        return f"Sucesso simulado para a referência: {ref_id}. Pode voltar ao formulário!"
    return "Referência não encontrada", 404

@app.route('/descarregar-pdf/<ref_id>', methods=['GET'])
def descarregar_pdf(ref_id):
    if TRANSACCOES.get(ref_id) != "PAID":
        return "Acesso bloqueado. O pagamento não foi confirmado.", 403

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Circle

    dados = DADOS_CV.get(ref_id)
    buffer = io.BytesIO()
    
    # Margens estreitas para optimizar o layout de duas colunas
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    
    cor_principal = colors.HexColor(dados['cor'])
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=22, textColor=cor_principal, spaceAfter=2)
    sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4a5568'), fontName='Helvetica-Bold', spaceAfter=12)
    side_h = ParagraphStyle('SH', parent=styles['Normal'], fontSize=11, textColor=cor_principal, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5)
    side_b = ParagraphStyle('SB', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#2d3748'))
    main_h = ParagraphStyle('MH', parent=styles['Heading2'], fontSize=12, textColor=cor_principal, spaceBefore=12, spaceAfter=5)
    main_b = ParagraphStyle('MB', parent=styles['BodyText'], fontSize=9.5, leading=14, textColor=colors.HexColor('#333333'))

    # Desenho das bolinhas gráficas para as competências no PDF
    def pontos_nivel(nv):
        d = Drawing(60, 10)
        for i in range(5):
            c = cor_principal if i < nv else colors.HexColor('#e2e8f0')
            d.add(Circle(5 + (i * 12), 5, 4, fillColor=c, strokeColor=None))
        return d

    # Coluna Esquerda (Dados e Competências)
    col_esquerda = [
        Paragraph("DADOS PESSOAIS", side_h),
        Paragraph(f"<b>Email:</b><br/>{dados['email']}", side_b),
        Spacer(1, 4),
        Paragraph(f"<b>Telefone:</b><br/>{dados['telefone_contacto']}", side_b),
    ]
    
    # Processar competências vindas do formulário
    linhas_comp = []
    if dados['competencias']:
        col_esquerda.append(Spacer(1, 10))
        col_esquerda.append(Paragraph("COMPETÊNCIAS", side_h))
        for linha in dados['competencias'].split('\n'):
            if ',' in linha:
                c, n = linha.split(',', 1)
                try:
                    linhas_comp.append([Paragraph(c.strip(), side_b), pontos_nivel(int(n.strip()))])
                except: pass
        if linhas_comp:
            t_comp = Table(linhas_comp, colWidths=[100, 60])
            t_comp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
            col_esquerda.append(t_comp)

    # Coluna Direita (Nome, Perfil, Percurso)
    col_direita = [
        Paragraph(dados['nome'].upper(), title_style),
        Paragraph(dados['titulo'].upper(), sub_style),
    ]
    if dados['perfil']:
        col_direita.extend([Paragraph("PERFIL", main_h), Paragraph(dados['perfil'].replace('\n', '<br/>'), main_b)])
    col_direita.extend([Paragraph("EXPERIÊNCIA PROFISSIONAL", main_h), Paragraph(dados['experiencia'].replace('\n', '<br/>'), main_b)])
    col_direita.extend([Paragraph("EDUCAÇÃO E FORMAÇÃO", main_h), Paragraph(dados['educacao'].replace('\n', '<br/>'), main_b)])

    # Matriz Mestre do Layout
    tabela_mestre = Table([[col_esquerda, col_direita]], colWidths=[170, 380])
    tabela_mestre.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fcfaf7')),
        ('RIGHTPADDING', (0,0), (0,0), 10),
        ('LEFTPADDING', (1,0), (1,0), 15),
        ('LINEAFTER', (0,0), (0,0), 1, colors.HexColor('#e2e8f0')),
    ]))
    
    doc.build([tabela_mestre])
    buffer.seek(0)

    # Limpeza da cache de dados
    TRANSACCOES.pop(ref_id, None)
    DADOS_CV.pop(ref_id, None)

    return send_file(buffer, as_attachment=True, download_name="Curriculo_Premium.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)


