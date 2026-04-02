# Como Instalar o Painel FS2024 Configurator

Este é um guia simples para instalar o software do painel no seu PC.

## Pré-requisitos
- Windows 10 ou Windows 11
- Porta USB livre (para conectar o painel Arduino)

## Passo 1: Download do Software

1. Localize o arquivo `PainelFS2024-Configurator.exe` na pasta `dist/`
2. Copie este arquivo para uma pasta permanente no seu computador
   - **Recomendado:** `C:\Programas\PainelFS2024\` ou `C:\Users\[SeuNome]\Desktop\`

## Passo 2: Conectar o Hardware

**Antes de executar o software:**
1. Conecte o painel Arduino à porta USB do computador
2. Aguarde 2-3 segundos para o Windows reconhecer o dispositivo
3. Se aparecer um aviso de "SmartScreen" (veja abaixo), clique em "Mais informações" e depois "Executar assim mesmo"

## Passo 3: Executar o Software

1. **Duplo clique** no arquivo `PainelFS2024-Configurator.exe`
2. A janela do configurador abrirá automaticamente
3. Verifique que a porta COM foi detectada (será mostrada automaticamente na seção "Conexão")

## Passo 4: Usar o Painel

### Na primeira execução:
- O software detectará automaticamente a porta COM do painel
- As configurações serão salvas e carregarão automaticamente na próxima vez

### Funcionalidades principais:
- **Conexão Serial:** Conecta/desconecta do painel
- **Frequências:** Mostra ACT/STBY do MSFS 2024 no LCD do painel
- **Auto MSFS:** Sincroniza automaticamente com o simulador quando habilitado
- **Perfis:** Salve suas configurações de frequência favoritas
- **Tema:** Mude entre modo claro, escuro ou automático (acompanha seu Windows)

## Resolução de Problemas

### "SmartScreen impediu o início deste aplicativo"
- **Solução:** Clique em "Mais informações" → "Executar assim mesmo"
- Este aviso é normal para software baixado da internet; nosso software é seguro

### "Porta COM não detectada"
- Verifique se o cabo USB está bem conectado
- Desconecte e reconecte o painel
- Aguarde 3 segundos e tente novamente
- Se persistir, verifique se o Arduino Leonardo foi reconhecido pelos drivers do Windows

### "Conexão recusada" ou "Erro de conexão"
- Verifique se o painel está ligado corretamente
- Feche o confitgurador, desconecte e reconecte o painel, e abra novamente
- Se o problema persistir, seu pai pode me contatar

### "A tela fica branca/congelada"
- Feche a janela (clique X)
- Se ficar preso na bandeja do sistema (canto inferior direito), clique no ícone e selecione "Sair"

## Modo Bandeja (Tray)

O software pode ser minimizado para a bandeja do sistema (canto inferior direito):
- **Clique no botão minimizar:** O app continua rodando mas fica oculto
- **Clique no ícone na bandeja:** Abre ou volta para minimizado
- **Menu de tray:** Clique com botão direito no ícone para ver opções

## Cópia de Segurança das Configurações

Suas configurações e perfis são salvos em:
```
C:\Users\[SeuNome]\AppData\Roaming\PainelFS2024\
```

Importante: Esta pasta é criada automaticamente na primeira execução. Se quiser fazer backup:
1. Abra o Explorador de Arquivos
2. Cole o caminho acima na barra de endereço
3. Copie os arquivos `settings.json` e `profiles.json` para um backup

## Atualizar o Software

Quando uma nova versão estiver disponível:
1. Faça backup dos seus perfis (veja acima)
2. Baixe o novo `PainelFS2024-Configurator.exe` e subsitua o antigo
3. Execute normalmente - suas configurações serão carregadas automaticamente

## Versão Instalada

Versão atual: **1.3.0** (última atualização: 02/04/2026 16:21)

Para verificar a versão instalada:
1. Abra o software
2. Clique em "Sobre" ou observe a titl

 bar da janela que mostra "Painel FS2024 Configurator"

## Suporte

Se encontrar qualquer problema:
1. Tente os passos de "Resolução de Problemas" acima
2. Desconecte o painel, reinicie o PC e tente novamente
3. Se persistir, salve uma captura de tela com a mensagem de erro e me envie

---

**Dica importante:** O software se conectará automaticamente ao painel sempre que for executado, e carregará sessão anterior (porta COM, tema, perfis). Você não precisa reconfiguar tudo de novo!
