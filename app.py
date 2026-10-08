<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Criador de Currículos Moçambique</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f4f8; margin: 0; padding: 0; display: flex; height: 100vh; }
        .formulario-bloco { width: 45%; background: white; padding: 25px; overflow-y: auto; border-right: 2px solid #cbd5e0; box-sizing: border-box; }
        .previsao-bloco { width: 55%; background: #cbd5e0; padding: 30px; display: flex; justify-content: center; overflow-y: auto; box-sizing: border-box; }
        .folha-a4 { width: 100%; max-width: 450px; background: white; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-radius: 4px; }
        input, textarea, select { width: 100%; padding: 10px; margin-top: 5px; margin-bottom: 12px; border: 1px solid #cbd5e0; border-radius: 6px; box-sizing: border-box; }
        .caixa-pagamento { background: #e6fffa; padding: 15px; border-radius: 6px; border-left: 5px solid #319795; }
        .btn-acao { width: 100%; background: #3182ce; color: white; padding: 12px; border: none; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; }
        .overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); color: white; text-align: center; padding-top: 150px; z-index: 3000; }
        .btn-teste { background: #e53e3e; color: white; padding: 10px 20px; border: none; font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>

<div class="overlay" id="janelaAguardar">
    <h2>🔄 Ordem Enviada para a Rede Móvel!</h2>
    <p>Se escolheu M-Pesa, aguarde o menu do **\*150#** no ecrã. Se escolheu e-Mola, aguarde o menu do **\*898#**.</p>
    <p>Introduza o seu PIN para confirmar a taxa de 50 MT.</p>
    <hr style="width:50%; margin: 20px auto; border-color:#4a5568;">
    <p style="font-size:14px; color:#cbd5e0;">[AMBIENTE DE TESTES] Clique abaixo para simular que o cliente já digitou o PIN no telemóvel:</p>
    <button class="btn-teste" id="btnSimularPin">Simular Confirmação de PIN (Aprovar)</button>
</div>

<div class="formulario-bloco">
    <h2>Dados do Currículo</h2>
    <form id="meuForm">
        <label>Nome Completo:</label>
        <input type="text" name="nome" id="iNome" value="Martílio Banze" oninput="aoDigitar()">
        
        <label>Título Profissional:</label>
        <input type="text" name="titulo_professional" id="iTitulo" value="Administrador de Sistemas & Cientista de Dados" oninput="aoDigitar()">

        <label>Email:</label>
        <input type="email" name="email" id="iEmail" value="martiliobanze@gmail.com" oninput="aoDigitar()">

        <label>Telefone de Contacto:</label>
        <input type="tel" name="telefone_contacto" id="iTelCont" value="844330181" oninput="aoDigitar()">

        <label>Resumo de Perfil:</label>
        <textarea name="perfil" id="iPerfil" rows="3" oninput="aoDigitar()">Especialista em HPC e computação distribuída.</textarea>

        <label>Experiência Profissional:</label>
        <textarea name="experiencia" id="iExp" rows="3" oninput="aoDigitar()">HPC Systems Administrator (2022-Actualidade) - MCTD/MoRENet</textarea>

        <label>Educação:</label>
        <textarea name="educacao" id="iEdu" rows="2" oninput="aoDigitar()">Licenciatura em Meteorologia - UEM</textarea>

        <label>Cor do Layout:</label>
        <select name="cor" id="iCor" onchange="aoDigitar()">
            <option value="#1a365d">Azul Marinho</option>
            <option value="#9b2c2c">Vermelho Escuro</option>
            <option value="#234e52">Verde Petróleo</option>
        </select>

        <div class="caixa-pagamento">
            <h3>Pagamento Seguro via USSD Push</h3>
            <label>Escolha o Método:</label>
            <select name="carteira">
                <option value="mpesa">M-Pesa (*150#) - Conta: 844330181</option>
                <option value="emola">e-Mola (*898#) - Conta: 861010333</option>
            </select>
            <label>Número do Telemóvel que vai Pagar:</label>
            <input type="tel" name="telefone" placeholder="84XXXXXXX ou 86XXXXXXX" required>
        </div>

        <button type="button" class="btn-acao" style="margin-top:15px;" onclick="enviarFormulario()">Pagar e Descarregar CV</button>
    </form>
</div>

<div class="previsao-bloco">
    <div class="folha-a4">
        <h1 id="vNome" style="margin:0; uppercase;">-</h1>
        <h3 id="vTitulo" style="margin:0; color:#718096; font-size:14px;">-</h3>
        <p><b>Email:</b> <span id="vEmail">-</span> | <b>Tel:</b> <span id="vTel">-</span></p>
        <hr>
        <h4>PERFIL</h4>
        <p id="vPerfil" style="white-space: pre-line; font-size:13px; color:#4a5568;"></p>
        <h4>EXPERIÊNCIA PROFISSIONAL</h4>
        <p id="vExp" style="white-space: pre-line; font-size:13px; color:#4a5568;"></p>
        <h4>EDUCAÇÃO</h4>
        <p id="vEdu" style="white-space: pre-line; font-size:13px; color:#4a5568;"></p>
    </div>
</div>

<script>
function aoDigitar() {
    const cor = document.getElementById('iCor').value;
    document.getElementById('vNome').innerText = document.getElementById('iNome').value;
    document.getElementById('vNome').style.color = cor;
    document.getElementById('vTitulo').innerText = document.getElementById('iTitulo').value;
    document.getElementById('vEmail').innerText = document.getElementById('iEmail').value;
    document.getElementById('vTel').innerText = document.getElementById('iTelCont').value;
    document.getElementById('vPerfil').innerText = document.getElementById('iPerfil').value;
    document.getElementById('vExp').innerText = document.getElementById('iExp').value;
    document.getElementById('vEdu').innerText = document.getElementById('iEdu').value;
}

let verificarIntervalo;

function enviarFormulario() {
    const form = document.getElementById('meuForm');
    document.getElementById('janelaAguardar').style.display = 'block';

    fetch('/iniciar-pagamento', {
        method: 'POST',
        body: new FormData(form)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === "SUCCESS") {
            const ref = data.ref;
            
            // Configura o botão vermelho de teste para simular o PIN com a referência correta
            document.getElementById('btnSimularPin').onclick = function() {
                fetch(`/confirmar-pagamento-teste/${ref}`)
                .then(res => res.json())
                .then(resData => {
                    alert(resData.message);
                });
            };

            // Inicia a escuta em segundo plano (polling de 3 em 3 segundos)
            verificarIntervalo = setInterval(() => {
                fetch(`/checar-status/${ref}`)
                .then(res => res.json())
                .then(statusData => {
                    if(statusData.status === "PAID") {
                        clearInterval(verificarIntervalo);
                        document.getElementById('janelaAguardar').style.display = 'none';
                        window.location.href = `/descarregar-pdf/${ref}`;
                    }
                });
            }, 3000);
        }
    });
}

window.onload = aoDigitar;
</script>

</body>
</html>


