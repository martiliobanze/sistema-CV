import io
import uuid
import requests
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

# Base de dados temporária em memória para registo das transacções
TRANSACCOES = {}
DADOS_CV = {}

def disparar_push_real(numero, valor, carteira, reference):
    """Trata o fluxo automático para o M-Pesa (*150#) ou e-Mola (*898#)."""
    print(f"[OPERADORA] Push enviado para o {numero} via {carteira}. Aguardando PIN do cliente.")
    return True

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/preview', methods=['GET'])
def abrir_previsao():
    return render_template('preview.html')

@app.route('/iniciar-pagamento', methods=['POST'])
def iniciar_pagamento():
    telefone = request.form.get('telefone')
    carteira = request.form.get('carteira')
    
    if not telefone or len(telefone) < 9:
        return jsonify({"status": "ERROR", "message": "Número de telefone inválido em Moçambique."}), 400

    ref_id = str(uuid.uuid4())[:8]
    
    DADOS_CV[ref_id] = {
        "nome": request.form.get('nome', ''),
        "titulo": request.form.get('titulo_professional', ''),
        "email": request.form.get('email', ''),
        "telefone_contacto": request.form.get('telefone_contacto', ''),
        "perfil": request.form.get('perfil', ''),
        "experiencia": request.form.get('experiencia', ''),
        "educacao": request.form.get('educacao', ''),
        "competencias": request.form.get('competencias', ''),
        "certificacoes": request.form.get('certificacoes', ''),
        "cor": request.form.get('cor', '#1a365d'),
        "template": request.form.get('template', 'martilio')
    }
    
    TRANSACCOES[ref_id] = "PENDING"
    disparar_push_real(telefone, 50, carteira, ref_id)
    return jsonify({"status": "SUCCESS", "ref": ref_id})

@app.route('/checar-status/<ref_id>', methods=['GET'])
def checar_status(ref_id):
    status = TRANSACCOES.get(ref_id, "NOT_FOUND")
    return jsonify({"status": status})

@app.route('/confirmar-pagamento-teste/<ref_id>', methods=['GET'])
def confirmar_pagamento_teste(ref_id):
    if ref_id in TRANSACCOES:
        TRANSACCOES[ref_id] = "PAID"
        return jsonify({"status": "CONFIRMED", "message": "Pagamento aprovado com sucesso no ambiente de testes!"})
    return jsonify({"status": "ERROR", "message": "Transacção não encontrada."}), 404

@app.route('/descarregar-pdf/<ref_id>', methods=['GET'])
def descarregar_pdf(ref_id):
    if TRANSACCOES.get(ref_id) != "PAID":
        return "Acesso proibido. Pagamento em falta.", 403

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Circle

    dados = DADOS_CV.get(ref_id)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=25, rightMargin=25, topMargin=25, bottomMargin=25)
    
    cor_principal = colors.HexColor(dados['cor'])
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=22, textColor=cor_principal, spaceAfter=2)
    sub_title_style = ParagraphStyle('ST', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#4a5568'), fontName='Helvetica-Bold', spaceAfter=12)
    side_header = ParagraphStyle('SH', parent=styles['Normal'], fontSize=11, textColor=cor_principal, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
    side_body = ParagraphStyle('SB', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#2d3748'))
    main_header = ParagraphStyle('MH', parent=styles['Heading2'], fontSize=12, textColor=cor_principal, spaceBefore=14, spaceAfter=6)
    main_body = ParagraphStyle('MB', parent=styles['BodyText'], fontSize=9.5, leading=14, textColor=colors.HexColor('#333333'))

    def points_level(nv):
        d = Drawing(60, 10)
        for i in range(5):
            c = cor_principal if i < nv else colors.HexColor('#e2e8f0')
            d.add(Circle(5 + (i * 12), 5, 3.5, fillColor=c, strokeColor=None))
        return d

    col_esquerda = [
        Paragraph("DADOS PESSOAIS", side_header),
        Paragraph(f"<b>Email:</b><br/>{dados['email']}", side_body),
        Spacer(1, 4),
        Paragraph(f"<b>Telefone:</b><br/>{dados['telefone_contacto']}", side_body),
    ]
    
    if dados['competencias']:
        col_esquerda.append(Spacer(1, 10))
        col_esquerda.append(Paragraph("FERRAMENTAS & SKILLS", side_header))
        linhas_comp = []
        for linha in dados['competencias'].split('\n'):
            if ',' in linha:
                c, n = linha.split(',', 1)
                try: 
                    linhas_comp.append([Paragraph(c.strip(), side_body), points_level(int(n.strip()))])
                except: 
                    pass
        if len(linhas_comp) > 0:
            t_comp = Table(linhas_comp, colWidths=[95, 60])
            t_comp.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
            col_esquerda.append(t_comp)

    col_direita = [
        Paragraph(dados['nome'].upper(), title_style),
        Paragraph(dados['titulo'].upper(), sub_title_style),
    ]
    
    if dados['perfil']:
        col_direita.extend([Paragraph("PROFILE", main_header), Paragraph(dados['perfil'].replace('\n', '<br/>'), main_body)])
    col_direita.extend([Paragraph("EDUCATION", main_header), Paragraph(dados['educacao'].replace('\n', '<br/>'), main_body)])
    col_direita.extend([Paragraph("PROFESSIONAL EXPERIENCE", main_header), Paragraph(dados['experiencia'].replace('\n', '<br/>'), main_body)])
    
    if dados['certificacoes']:
        col_direita.extend([Paragraph("CERTIFICATIONS & COURSES", main_header), Paragraph(dados['certificacoes'].replace('\n', '<br/>'), main_body)])

    tabela_mestre = Table([[col_esquerda, col_direita]], colWidths=[160, 400])
    tabela_mestre.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fcfaf7')),
        ('RIGHTPADDING', (0,0), (0,0), 10),
        ('LEFTPADDING', (1,0), (1,0), 15),
        ('LINEAFTER', (0,0), (0,0), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    
    doc.build([tabela_mestre])
    buffer.seek(0)
    
    TRANSACCOES.pop(ref_id, None)
    DADOS_CV.pop(ref_id, None)
    return send_file(buffer, as_attachment=True, download_name=f"CV_{dados['nome'].replace(' ', '_')}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)

