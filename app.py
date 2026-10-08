<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização Real em Duas Colunas</title>
    <style>
        body { font-family: Arial, sans-serif; background: #cbd5e0; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .folha-a4 { width: 210mm; min-height: 275mm; background: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border-radius: 4px; display: flex; box-sizing: border-box; overflow: hidden; }
        .col-lateral { width: 30%; background: #fcfaf7; border-right: 1px solid #cbd5e0; padding: 20px; box-sizing: border-box; }
        .col-principal { width: 70%; padding: 30px; box-sizing: border-box; }
        h1 { margin: 0; text-transform: uppercase; font-size: 22px; }
        h3 { margin: 4px 0 15px 0; color: #4a5568; font-size: 13px; font-weight: bold; }
        .seccao-h { font-size: 12px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 2px; }
        .txt { font-size: 11px; color: #2d3748; line-height: 1.5; white-space: pre-line; margin-top: 5px; }
    </style>
</head>
<body>

    <div class="folha-a4">
        <!-- Coluna Esquerda (Contactos e Skills) -->
        <div class="col-lateral">
            <div class="seccao-h" id="hL1">DADOS PESSOAIS</div>
            <p style="margin:10px 0 2px 0; font-size:11px; font-weight:bold;">Email:</p>
            <div id="vEmail" style="font-size:10px; word-break:break-all;">-</div>
            <p style="margin:8px 0 2px 0; font-size:11px; font-weight:bold;">Telefone:</p>
            <div id="vTel" style="font-size:10px;">-</div>
            
            <div class="seccao-h" id="hL2">FERRAMENTAS & SKILLS</div>
            <div id="vCompLista" style="margin-top:8px; font-size:11px;"></div>
        </div>
        
        <!-- Coluna Direita (Histórico) -->
        <div class="col-principal">
            <h1 id="vNome">-</h1>
            <h3 id="vTitulo">-</h3>
            
            <div class="seccao-h" id="h1">PROFILE</div>
            <div class="txt" id="vPerfil">-</div>
            
            <div class="seccao-h" id="h2">EDUCATION</div>
            <div class="txt" id="vEdu">-</div>
            
            <div class="seccao-h" id="h3">PROFESSIONAL EXPERIENCE</div>
            <div class="txt" id="vExp">-</div>

            <div class="seccao-h" id="h4">CERTIFICATIONS & COURSES</div>
            <div class="txt" id="vCert">-</div>
        </div>
    </div>

<script>
    const canal = new BroadcastChannel('cv_canal');
    canal.onmessage = (e) => {
        const d = e.data;
        document.getElementById('vNome').innerText = d.nome;
        document.getElementById('vNome').style.color = d.cor;
        document.getElementById('vTitulo').innerText = d.titulo;
        document.getElementById('vEmail').innerText = d.email;
        document.getElementById('vTel').innerText = d.telefone_contacto;
        document.getElementById('vPerfil').innerText = d.perfil;
        document.getElementById('vEdu').innerText = d.educacao;
        document.getElementById('vExp').innerText = d.experiencia;
        document.getElementById('vCert').innerText = d.certificacoes;
        
        ['hL1', 'hL2', 'h1', 'h2', 'h3', 'h4'].forEach(id => {
            document.getElementById(id).style.color = d.cor;
            document.getElementById(id).style.borderBottomColor = d.cor;
        });

        const listaAlvo = document.getElementById('vCompLista');
        listaAlvo.innerHTML = '';
        if(d.competencias) {
            d.competencias.split('\n').forEach(l => {
                if(l.includes(',')) {
                    const [n, nv] = l.split(',');
                    let pts = '';
                    for(let i=0; i<5; i++) pts += i < parseInt(nv) ? '●' : '○';
                    const item = document.createElement('div');
                    item.style.marginBottom = '5px';
                    item.innerHTML = `<div style="display:flex; justify-content:space-between;"><span>${n.trim()}</span><span style="color:${d.cor}; font-size:9px;">${pts}</span></div>`;
                    listaAlvo.appendChild(item);
                }
            });
        }
    };
</script>
</body>
</html>
