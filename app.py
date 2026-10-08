import io
import uuid
import requests
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

# Base de dados temporária em memória para registo das transacções
TRANSACCOES = {}
DADOS_CV = {}

def disparar_push_real(numero, valor, carteira, reference):
    """
    Comunica com o gateway de pagamentos móveis em Moçambique.
    Trata o fluxo automático para o M-Pesa (*150#) ou e-Mola (*898#).
    """
    # Enquanto estiver em testes, o sistema aceita o pedido e aguarda o PIN simulado.
    # Quando possuir as chaves comerciais da Vodacom/Movitel, descomente o bloco abaixo:
    """
    url_gateway = "https://vm.co.mz" if carteira == 'mpesa' else "https://movitel.co.mz"
    headers = {"Authorization": "Bearer SEU_TOKEN_DE_ACESSO"}
    payload = {
        "amount": str(valor),
        "msisdn": numero,
        "reference": reference,
        "thirdPartyReference": reference
    }
    try:
        response = requests.post(url_gateway, json=payload, headers=headers)
        return response.status_code == 200
    except:
        return False
    """
    print(f"[OPERADORA] Push enviado para o {numero} via {carteira}. Aguardando PIN do cliente.")
    return True

@app.route('/', methods=['GET'])
def index():
    """Rota principal que entrega o formulário de preenchimento."""
    return render_template('index.html')

@app.route('/preview', methods=['GET'])
def abrir_previsao():
    """Rota que entrega a folha de visualização numa aba independente."""
    return render_template('preview.html')

@app.route('/iniciar-pagamento', methods=['POST'])
def iniciar_pagamento():
    """Etapa 1: Regista os dados do utilizador e despoleta o pedido de PIN."""
    telefone = request.form.get('telefone')
    carteira = request.form.get('carteira')
    
    if not telefone or len(telefone) < 9:
        return jsonify({"status": "ERROR", "message": "Número de telefone inválido em Moçambique."}), 400

    ref_id = str(uuid.uuid4())[:8] # Cria um identificador curto de transacção
    
    # Guarda de forma estruturada todos os dados para a posterior criação do PDF
    DADOS_CV[ref_id] = {
        "nome": request.form.get('nome', ''),
        "titulo": request.form.get('titulo_professional', ''),
        "email": request.form.get('email', ''),
        "telefone_contacto": request.form.get('telefone_contacto', ''),
        "perfil": request.form.get('perfil', ''),
        "experiencia": request.form.get('experiencia', ''),
        "educacao": request.form.get('educacao', ''),
        "cor": request.form.get('cor', '#1a365d')
    }
    
    # Define o estado da operação como pendente
    TRANSACCOES[ref_id] = "PENDING"
    
    # Dispara a cobrança automática para o telemóvel
    cobranca_disparada = disparar_push_real(telefone, 50, carteira, ref_id)
    
    if not cobranca_disparada:
        return jsonify({"status": "ERROR", "message": "Falha ao contactar a rede móvel comercial."}), 500
        
    return jsonify({"status": "SUCCESS", "ref": ref_id})

@app.route('/checar-status/<ref_id>', methods=['GET'])
def checar_status(ref_id):
    """O JavaScript consulta esta rota de 3 em 3 segundos para validar o PIN."""
    status = TRANSACCOES.get(ref_id, "NOT_FOUND")
    return jsonify({"status": status})

@app.route('/confirmar-pagamento-teste/<ref_id>', methods=['GET'])
def confirmar_pagamento_teste(ref_id):
    """Rota de simulação para aprovação manual no ambiente de testes."""
    if ref_id in TRANSACCOES:
        TRANSACCOES[ref_id] = "PAID"
        return jsonify({"status": "CONFIRMED", "message": "Pagamento aprovado com sucesso no ambiente de testes!"})
    return jsonify({"status": "ERROR", "message": "Transacção não encontrada."}), 404

@app.route('/descarregar-pdf/<ref_id>', methods=['GET'])
def descarregar_pdf(ref_id):
    """Compila os dados recolhidos e liberta o download do PDF apenas se estiver pago."""
    if TRANSACCOES.get(ref_id) != "PAID":
        return "Acesso proibido. O pagamento ainda não foi processado pelo sistema.", 403

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    dados = DADOS_CV.get(ref_id)
    buffer = io.BytesIO()
    
    # Configuração física do documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    
    cor_principal = colors.HexColor(dados['cor'])
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=22, textColor=cor_principal)
    body_style = ParagraphStyle('B', parent=styles['BodyText'], fontSize=10, leading=14)
    header_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=cor_principal, spaceBefore=10)

    # Construção gráfica da coluna de contactos (Esquerda)
    col_esquerda = [
        Paragraph("<b>CONTACTOS</b>", header_style),
        Paragraph(f"Email: {dados['email']}", body_style),
        Paragraph(f"Telefone: {dados['telefone_contacto']}", body_style),
    ]
    
    # Construção gráfica da coluna de percurso (Direita)
    col_direita = [
        Paragraph(dados['nome'].upper(), title_style),
        Paragraph(dados['titulo'].upper(), body_style),
        Spacer(1, 10),
        Paragraph("<b>PERFIL</b>", header_style),
        Paragraph(dados['perfil'].replace('\n', '<br/>'), body_style),
        Paragraph("<b>EXPERIÊNCIA PROFISSIONAL</b>", header_style),
        Paragraph(dados['experiencia'].replace('\n', '<br/>'), body_style),
        Paragraph("<b>EDUCAÇÃO</b>", header_style),
        Paragraph(dados['educacao'].replace('\n', '<br/>'), body_style),
    ]

    # Montagem final do esqueleto de duas colunas
    tabela = Table([[col_esquerda, col_direita]], colWidths=[160, 360])
    tabela.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEAFTER', (0,0), (0,0), 1, colors.HexColor('#e2e8f0'))
    ]))
    
    doc.build([tabela])
    buffer.seek(0)

    # Eliminação dos dados em memória após a transferência por questões de segurança
    TRANSACCOES.pop(ref_id, None)
    DADOS_CV.pop(ref_id, None)

    return send_file(buffer, as_attachment=True, download_name="Curriculo_Profissional.pdf", mimetype='application/pdf')

@app.route('/webhook-carteiras', methods=['POST'])
def webhook_carteiras():
    """Webhook de produção: Recebe os avisos em segundo plano da Vodacom/Movitel."""
    dados = request.get_json()
    if dados and (dados.get('status') == 'SUCCESS' or dados.get('output_ResponseCode') == 'INS-0'):
        ref_id = dados.get('reference') or dados.get('output_ThirdPartyReference')
        if ref_id in TRANSACCOES:
            TRANSACCOES[ref_id] = "PAID"
            return jsonify({"status": "ACCEPTED"}), 200
    return jsonify({"status": "DECLINED"}), 400

if __name__ == '__main__':
    app.run(debug=True)

