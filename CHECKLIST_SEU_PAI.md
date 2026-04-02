# CHECKLIST PARA INSTALAÇÃO DO PAINEL - Seu Pai

Siga este checklist passo-a-passo. Se tudo der certo, seu painel estará 100% funcional!

## ✅ ANTES DE INSTALAR

- [ ] Windows 10 ou 11 instalado
- [ ] Painel Arduino Leonardo pronto
- [ ] Cabo USB disponível
- [ ] Porta USB no computador
- [ ] Arquivo `PainelFS2024-Configurator.exe` baixado

## 📥 INSTALAÇÃO

- [ ] Copie o arquivo `PainelFS2024-Configurator.exe` para uma pasta permanente
    - Sugerido: `C:\Users\[SeuNome]\Desktop\` ou `C:\Programas\PainelFS2024\`
- [ ] **Não deixe** em `Downloads` (pode ser apagado depois)
- [ ] Não renomeie o arquivo (deixe como `PainelFS2024-Configurator.exe`)

## 🔌 HARDWARE

- [ ] Desconecte qualquer outro Arduino do computador (opcional, mas recomendado)
- [ ] Conecte o painel Arduino na porta USB
- [ ] Aguarde 2-3 segundos (Windows reconhecendo o dispositivo)
- [ ] Não desconecte durante a execução

## ▶️ PRIMEIRA EXECUÇÃO

- [ ] Duplo clique no arquivo `PainelFS2024-Configurator.exe`
- [ ] Se aparecer o aviso de SmartScreen:
    - [ ] Clique em "Mais informações"
    - [ ] Clique em "Executar assim mesmo"
- [ ] A janela do software abrirá
- [ ] **Pode levar 3-5 segundos** na primeira vez

## 👀 VERIFICAÇÃO PÓS-ABERTURA

Dentro da janela do software, verifique:

### Seção "Conexão Serial"
- [ ] Campo "Porta COM" mostra um valor (ex: `COM3`, `COM5`)
- [ ] Se não mostrar nada, aguarde 3 segundos e tente novamente
- [ ] Status mostra "Conectado" em verde

### Seção "Frequências"
- [ ] Campo "ACT" mostra um valor (ex: `121.750`)
- [ ] Campo "STBY" mostra um valor (ex: `124.850`)
- [ ] Se não mostrar, clique em "Conectar" na seção de Conexão

### LCD do Painel
- [ ] A primeira linha do LCD acende
- [ ] Mostra as frequências (ex: `121.750 | 124.850`)

## 🎨 APARÊNCIA (Opcional)

- [ ] Escolha um tema:
    - **Sistema:** segue configuração do Windows
    - **Claro:** fundo branco
    - **Escuro:** fundo escuro
- [ ] O tema salva automaticamente

## 🎮 TESTE RÁPIDO (Se MSFS 2024 Instalado)

- [ ] Abra MSFS 2024
- [ ] Escolha qualquer aeronave que tenha rádio VHF
- [ ] Mude a frequência ativa (ACT) em MSFS
- [ ] Verifique se o LCD do painel **atualiza automaticamente**
- [ ] Se sim: ✅ Tudo funcionando!

## 💾 CONFIGURAÇÕES

- [ ] O software **salva automaticamente** suas configurações
- [ ] Próxima vez que executar:
    - [ ] Mesma porta COM será conectada
    - [ ] Mesmo tema será aplicado
    - [ ] Tudo igual à última vez

## 🆘 SE ALGO NÃO FUNCIONAR

Se a porta COM não aparecer:
1. [ ] Desconecte o painel
2. [ ] Aguarde 3 segundos
3. [ ] Reconecte o painel
4. [ ] Clique em "Conectar" novamente
5. [ ] Se ainda não funcionar, verifique outro cabo USB

Se o LCD não acende:
1. [ ] Verifique conexão do LCD no painel (I2C)
2. [ ] Tente outro porto USB do computador
3. [ ] Reinicie o computador e tente novamente

Se o software congela:
1. [ ] Clique no X para fechar a janela
2. [ ] Se ficar preso, clique com botão direito na bandeja e escolha "Sair"
3. [ ] Abra novamente

## 📊 FUNCIONAMENTO NORMAL

Após a primeira execução com sucesso:

- [ ] Abra o software quando quiser usar o painel
- [ ] Software conecta automaticamente
- [ ] Use o MSFS 2024 normalmente
- [ ] LCD do painel atualiza em tempo real
- [ ] Fechue o software quando terminar

## 🔄 PRÓXIMAS VEZES

- [ ] Execute o arquivo `PainelFS2024-Configurator.exe`
- [ ] Tudo conecta automaticamente
- [ ] Suas configurações são carregadas
- [ ] Nenhuma reconfiguraç ão necessária

## 📝 IMPORTANTE

- ✅ Versão instalada: **1.3.0** (última versão segura)
- ✅ Build date: 02/04/2026 16:21
- ✅ Todas as correções de segurança aplicadas
- ✅ Pronto para uso a longo prazo

## 🎉 SUCESSO!

Se chegou até aqui e tudo funcionou, seu painel está 100% operacional!

Se tiver dúvidas, me procure com esta informação:
- Qual seção do checklist não funcionou?
- O que aparece na tela quando tenta conectar?

---

**Data:** 02/04/2026
**Versão do Software:** 1.3.0
**Status:** ✅ PRONTO PARA USO
