import io
import requests  # Permite ao Python comunicar com as APIs das operadoras
from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

# CONFIGURAÇÕES DAS SUAS CONTAS COMERCIAIS
CONTA_MPESA_RECEBEDORA = "844330181"  # Associada ao seu Shortcode comercial
CONTA_EMOLA_RECEBEDORA = "861010333"  # Associada às suas credenciais Movitel

# Dicionário temporário em memória para registar pagamentos aprovados pelos Webhooks
# Numa fase avançada, isto deve ser substituído por uma Base de Dados (ex: PostgreSQL)
PAGAMENTOS_APROVADOS = {}

def disparar_stk_push(numero_cliente, valor, carteira, transaccao_id):
    """
    Função que comunica directamente com a API da Vodacom ou Movitel 
    para fazer aparecer o pedido de PIN no telemóvel do cliente.
    """
    try:
        if carteira == 'mpesa':
            # Exemplo de chamada para a API oficial do M-Pesa Moçambique
            url_api = "https://vm.co.mz"
            headers = {
                "Authorization": "Bearer SEU_TOKEN_M_PESA",
                "Content-Type": "application/json"
            }
            payload = {
                "input_TransactionReference": transaccao_id,
                "input_CustomerMSISDN": numero_cliente,
                "input_Amount": str(valor),
                "input_ThirdPartyReference": transaccao_id,
                "input_ServiceProviderCode": "SEU_SHORTCODE_VODACOM"
            }
            # requests.post(url_api, json=payload, headers=headers)
            print(f"[M-Pesa] STK Push enviado para {numero_cliente}")
            return True

        elif carteira == 'emola':
            # Exemplo de chamada para a API do e-Mola ou Agregador e2Payments
            url_api = "https://explicador.co.mz"
            payload = {
                "client_id": "SEU_CLIENT_ID",
                "amount": valor,
                "phone": numero_cliente
            }
            print(f"[e-Mola] USSD Push enviado para {numero_cliente}")
            return True
            
    except Exception as e:
        print(f"Erro ao comunicar com a operadora: {e}")
        return False
        
    return True # Retorna True por defeito para testes enquanto não insere as chaves reais

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/gerar-cv', methods=['POST'])
def iniciar_processo_cv():
    """
    Esta rota inicia o processo. Recolhe os dados, solicita o PIN no telemóvel
    e aguarda a resposta automática do pagamento.
    """
    nome = request.form.get('nome')
    telefone_cliente = request.form.get('telefone')
    carteira = request.form.get('carteira')
    experiencia = request.form.get('experiencia')
    educacao = request.form.get('educacao')
    template_escolhido = request.form.get('template', 'classico')
    cor_hex = request.form.get('cor', '#1a365d')
    
    # Criamos um identificador único para esta transacção (usando o número do cliente temporariamente)
    transaccao_id = f"TX_{telefone_cliente}"
    preco_cv = 50 

    # Dispara o pedido automático de PIN para o telemóvel do cliente
    envio_pedido = disparar_stk_push(telefone_cliente, preco_cv, carteira, transaccao_id)

    if not envio_pedido:
        return "Erro ao iniciar o processo de cobrança com a operadora.", 500

    # SIMULAÇÃO DE PRODUÇÃO: Como estamos em fase de testes e desenvolvimento, 
    # forçamos a aprovação imediata para que possa ver o PDF a ser gerado.
    PAGAMENTOS_APROVADOS[transaccao_id] = True

    # Verifica se a transacção já foi dada como paga pelo Webhook da operadora
    if not PAGAMENTOS_APROVADOS.get(transaccao_id):
        return "A aguardar a confirmação do pagamento. Por favor, introduza o seu PIN no telemóvel e tente novamente.", 402

    # --- PROCESSAMENTO DO PDF ---
    foto_file = request.files.get('foto')
    foto_img = None
    if foto_file and foto_file.filename != '':
        try:
            foto_data = io.BytesIO(foto_file.read())
            foto_img = Image(foto_data, width=80, height=100)
        except Exception:
            foto_img = None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    cor_principal = colors.HexColor(cor_hex)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=24, textColor=cor_principal, spaceAfter=5)
    section_style = ParagraphStyle('Seccao', parent=styles['Heading2'], fontSize=13, textColor=cor_principal, spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle('Corpo', parent=styles['BodyText'], fontSize=10, leading=14, textColor=colors.HexColor('#333333'))

    elementos = []
    bloco_nome = [Paragraph(nome.upper(), title_style), Paragraph(f"<b>Contacto:</b> {telefone_cliente}", body_style)]

    if template_escolhido == 'moderno':
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
        tabela_layout = Table([[col_esquerda, col_direita]], colWidths=[180, 350])
        tabela_layout.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('RIGHTPADDING', (0,0), (0,0), 15),
            ('LEFTPADDING', (1,0), (1,0), 15),
            ('LINEAFTER', (0,0), (0,0), 1, cor_principal),
        ]))
        elementos.append(tabela_layout)
    else:
        if foto_img:
            tabela_cabecalho = Table([[bloco_nome, foto_img]], colWidths=[430, 100])
            tabela_cabecalho.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
            elementos.append(tabela_cabecalho)
        else:
            elementos.extend(bloco_nome)
        elementos.append(Spacer(1, 15))
        elementos.append(Paragraph("Experiência Profissional", section_style))
        elementos.append(Paragraph(experiencia.replace('\n', '<br/>'), body_style))
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph("Educação / Formação", section_style))
        elementos.append(Paragraph(educacao.replace('\n', '<br/>'), body_style))

    doc.build(elementos)
    buffer.seek(0)

    # Remove o registo de memória após o uso para protecção de dados
    PAGAMENTOS_APROVADOS.pop(transaccao_id, None)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CV_{nome.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

# --- ROTAS DE WEBHOOK (NOTIFICAÇÃO AUTOMÁTICA DAS OPERADORAS) ---

@app.route('/webhook-mpesa', methods=['POST'])
def webhook_mpesa():
    """
    Rota invisível que a Vodacom vai contactar de forma automática 
    assim que o cliente digitar o PIN com sucesso.
    """
    dados = request.get_json()
    # A estrutura depende do protocolo da Vodacom (ResultCode 0 significa Sucesso)
    if dados and dados.get('output_ResponseCode') == 'INS-0':
        transaccao_id = dados.get('output_ThirdPartyReference')
        PAGAMENTOS_APROVADOS[transaccao_id] = True # Marca como pago no sistema!
        return jsonify({"status": "SUCCESS"}), 200
    return jsonify({"status": "FAILED"}), 400

@app.route('/webhook-emola', methods=['POST'])
def webhook_emola():
    """
    Rota invisível que a Movitel vai contactar de forma automática
    assim que o cliente confirmar o pagamento no e-Mola.
    """
    dados = request.get_json()
    if dados and dados.get('status') == 'PAID':
        transaccao_id = dados.get('ref')
        PAGAMENTOS_APROVADOS[transaccao_id] = True
        return jsonify({"message": "OK"}), 200
    return jsonify({"message": "ERROR"}), 400

if __name__ == '__main__':
    app.run(debug=True)

