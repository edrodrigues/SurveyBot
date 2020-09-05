from funcoesWhatsapp import * #importa as funções para comunicação com whatsapp
from funcoesDoBanco import * #importa as funções q se comunicam com o banco de dados
from funcoesQuestionario import * #importa as funções q processam o questionario


from flask import Flask, render_template, request, url_for, redirect
from twilio.rest import Client

import json
import random

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == 'GET' or request.method == 'POST': #se receber um GET ou um POST executa as intruções abaixo


        msgRec = request.form.get("Body") #variavel de post vinda do twilio (msg enviada pelo )
        num = request.form.get("From") #variavel de post vinda do twilio


        if msgRec is not None and num is not None: #verifica se a variavel msg e a variavel num tem algum valor, ou seja, se foram enviadas via request (verifica se o post veio do twilio - msg de whatsapp do usuario)
            #trata as requisicoes feitas via whatsapp


            records = buscaidUsuario(num) #busca pelo usuario no banco (busca pelo numero de telefone)

            #records = []

            if len(records) == 0: #verifica se o usuario ja esta cadastrado (se a pesquisa retornou algum registro)
                #enviaMsg("Olá, Você é novo por aqui!!!",num)
                enviaMsg("Olá...",num)

                flagSalva = salvaidUsuarioNoBanco(num) #salva o usuario no banco

                if flagSalva == 1: #verifica se o usuario foi salvo (analisa a resposta do banco)
                    #enviaMsg("Seu numero foi gravado em nosso sistema!!!",num)
                    enviaMsg("Aguarde, estamos buscando um questionário pra você...",num)

                    records = buscaFomularioNoBanco(False) #Busca por formularios (False -> pega todos os registros, no lugar de False poderia ser usada uma URL)

                    if len(records) >0: #verifica se existem formularios no banco

                        questoes = ""


                        """
                        # TRECHO NÃO TESTADO
                        #pega todos os questionarios do banco
                        for row in records:
                            questoes = questoes + row[1]
                            idQuestionario = str(row[0])
                            urlQuestionario = row[2]


                        #gera um numero aleatorio entre dentro do intervalo de questionarios existentes (escolhe um questionario aleatoriamente)
                        indexRand = random.randint(0, len(questoes)-1)

                        questoesLista = json.loads(questoes[indexRand]) #deserializa os dados

                        """

                        #pega a resposta vinda do banco de separa os campos (pega sempre o ultimo form cadastrado mo banco) questoes = questoes + row[1]
                        for row in records:
                            questoes = row[1]
                            idQuestionario = str(row[0])
                            urlQuestionario = row[2]


                        questoesLista = json.loads(questoes) #deserializa os dados

                        enviaMsg( "**** *Iniciando Questionário* ****",num)

                        #envia o titulo do form e a descrição (primeiro registro da lista (questionario), index 0)

                        if len(questoesLista[0][0]['tituloForm']) > 0:
                            enviaMsg( "_" + questoesLista[0][0]['tituloForm'] + "_",num)
                        else:
                            enviaMsg( "_Esse formulário não tem título_",num)


                        """
                        #Envia a descrição do Formulário (Usa-lo causa muita poluição de texto)
                        if len(questoesLista[0][0]['descricaoForm']) > 0:
                            enviaMsg( "_" + questoesLista[0][0]['descricaoForm'] + "_",num)
                        else:
                            enviaMsg( "_Esse formulário não tem descrição_",num)
                        """


                        questoesLista.pop(0) #remove o primeiro registro da lista (questionario)

                        #envia a primeira pergunta


                        #envia todas as msg q não forem perguntas (titulo seção ou descrição)
                        if questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                            while questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                                msg = formataMsgPergunta(questoesLista) #formata o texto da msg de acordo com o tipo de pergunta
                                enviaMsg(msg,num) #envia a msg com a pergunta para o whatsapp
                                questoesLista.pop(0) #remove o primeiro registro da lista (questionario)


                        msg = formataMsgPergunta(questoesLista) #formata o texto da msg de acordo com o tipo de pergunta


                        enviaMsg(msg,num) #envia a msg com a pergunta para o whatsapp


                        #salva o restante das questões na tabela referente ao usuario
                        perguntas = json.dumps(questoesLista) #serializa os dados pra salvar no banco

                        atualizaPerguntasUsuario(num, perguntas) #salva o restante das perguntas no registro do usuario


                    else:
                        #se não houver forms no banco envia essa msg
                        enviaMsg("Ops, estamos estamos sem formulários no momento, tente novamente mais tarde!!!",num)
                        deletaUsuarioPeloidUsuario(str(num)) #deleta o numero do banco e renicia o processo


                else:
                    #envia essa msg em caso de problema no banco
                    enviaMsg("Ops, estamos com problemas, tente novamente mais tarde!!!",num)

            else:
                #trata as msg de ususarios já cadastrados
                #enviaMsg("Bom te ver novamente!!!",num)


                #recupera os dados do banco (dados do usuario)
                for row in records:
                    respostas = row[2] #pega a lista de respostas do usuario
                    questoes = row[3] #pega a lista de questões do usuario


                respostasLista = json.loads(respostas) #deserializa os dados (a variavel records[2] guarda a lista de respostas no usuario)
                questoesLista = json.loads(questoes) #deserializa os dados (a variavel records[3] guarda a lista de questões no usuario)

                if len(questoesLista) > 1: #verifica se é o ultimo resgistro (msgFinal de agradecimento)


                    #envia todas as msg q não forem perguntas (titulo seção ou descrição)
                    if questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                        while questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                            #msg = formataMsgPergunta(questoesLista) #formata o texto da msg de acordo com o tipo de pergunta
                            #enviaMsg(msg,num) #envia a msg com a pergunta para o whatsapp
                            questoesLista.pop(0) #remove o primeiro registro da lista (questionario)



                    #analisa a resposta atualiza o banco (tabela usuarios, campos questões e respostas)
                    verifResp = verificaResposta(questoesLista, respostasLista, msgRec)


                    if verifResp[0] == True:

                        respostas = json.dumps(verifResp[1]) #serializa os dados pra salvar no banco (lista de respostas)
                        atualizaRespostasUsuario(num, respostas) #salva no banco a resposta recebida (digita pelo usuario)

                        questoesLista.pop(0) #remove a questão respondida
                        perguntas = json.dumps(questoesLista) #serializa os dados pra salvar no banco (lista de perguntaa)
                        atualizaPerguntasUsuario(num, perguntas) #salva no banco (tabela usuarios) a lista de questões atualizada

                        #apos o pop veririfica se ainda existem perguntas na lista (se igual a 1 tem apenas a msgFinal de agradecimento)
                        if len(questoesLista) > 1:

                            #envia todas as msg q não forem perguntas (titulo seção ou descrição)
                            if questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                                while questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
                                    msg = formataMsgPergunta(questoesLista) #formata o texto da msg de acordo com o tipo de pergunta
                                    enviaMsg(msg,num) #envia a msg com a pergunta para o whatsapp
                                    questoesLista.pop(0) #remove o primeiro registro da lista (questionario)


                            msg = formataMsgPergunta(questoesLista) #formata o texto da msg de acordo com o tipo de pergunta
                            enviaMsg(msg,num) #envia a msg com a pergunta para o whatsapp


                        else:


                            #verirfica se há alguma msgFinal de agradecimento
                            if len(questoesLista[0][0]['msgFinal']) > 0:
                                enviaMsg(questoesLista[0][0]['msgFinal'],num)
                            else:
                                enviaMsg("Obrigado!!!",num)

                            enviaMsg("No momento estamos sem mais perguntas, volte mais tarde, Obrigado!!!",num)

                            #chama a função que envia a resposta para o google
                            resp = enviaResposta(questoesLista[0][0]['url'],respostasLista)



                    else:

                        #Em caso de resposta incoerente com a pergunta envia aviso de erro
                        enviaMsg(verifResp[1],num)

                else:

                    """
                    #verirfica se há alguma msgFinal de agradecimento
                    if len(questoesLista[0][0]['msgFinal']) > 0:
                        enviaMsg(questoesLista[0][0]['msgFinal'],num)
                    else:
                        enviaMsg("Obrigado!!!",num)
                    """

                    enviaMsg("No momento estamos sem mais perguntas, volte mais tarde, Obrigado!!!",num)

                    ############################### ADM RESET ###################################
                    if msgRec == "123":
                        deletaUsuarioPeloidUsuario(str(num)) #deleta o numero do banco e renicia o processo
                        enviaMsg("Ok, você quer mais um questionário???",num)


        else:
            #se foi apenas um post para abrir o site, retorna o html
            return render_template('index.html');




#trata as requisições de POST para a pagina "processar"
@app.route("/processar", methods=["POST"])
def processar():

    botaoForm = request.form.get("botaoForm") #captura o botão pressionado (o name do botao)

    #pega o click do botao Extrair
    if botaoForm == 'Importar Questões':
        #pega a url do form e extrai as questões

        url = request.form['urlQuestionario'] #pega o valor do post (valor do textarea - name)

        #veririca se o campo url está vazio
        if len(url) > 0:

            urlTemp = '_' + url #usado para testar se o usuario copiou a URL completa

            #verifica se a url tem http:
            if urlTemp.find("http") == -1:
                return render_template('index.html', questionario = "Sua URL deve ter http", urlForm = url, scroll='inputURL') #volta ao index e escreve o erro no text area


            questoesLista = extraiQuestoes(url) #envia a url para extração das questões (pega o retorno da função, uma lista de dicionarios)

            #verifica algum erro retornado da função extraiQuestoes()
            if questoesLista == False: #em caso de erro na url
                return render_template('index.html', questionario = "Erro!, Verifique sua URL ou seu questionario", urlForm = url, scroll='inputURL') #volta ao index e escreve o erro no text area
            else:

                records = buscaFomularioNoBanco(str(url)) #verifica se o form ja está cadastrado

                questoesSinal = ""

                pickledList = json.dumps(questoesLista) #serializa os dados pra salvar no banco

                if len(records) > 0:
                    #se o formulario ja existir apenas atualiza os campos
                    atualizaFomularioNoBanco(str(url), pickledList)
                    questoesSinal = "Atualizado\n\n"
                else:
                    #se o formulario não existir salva no banco
                    salvafomularioNoBanco(str(url), pickledList)
                    questoesSinal = "Salvo\n\n"


                #le o banco e pega as questões salvas
                records = buscaFomularioNoBanco(str(url)) #le o form do banco

                if len(records) > 0: #verifica se o banco retornou alguma coisa

                    questoes = ""

                    #pega a resposta vinda do banco de separa os campos
                    for row in records:
                        questoes = questoes + row[1]
                        idQuestionario = str(row[0])
                        urlQuestionario = row[2]

                    questoes = json.loads(questoes) #deserializa os dados

                    questoesTemp = ""

                    #le cada uma das questões salvas no banco (não le o index 0 e nem o ultimo, que contem outroas informações)
                    for n in range(1, len(questoes)- 1):
                        questoesTemp  = questoesTemp + questoes[n][0]['pergunta'] + "\n"


                    return render_template('index.html', questionario = questoesSinal + questoesTemp, urlForm = url, scroll='inputURL') #volta ao index e escreve no text area

                else:

                    return render_template('index.html', questionario = "Houve algum problema no banco, tente mais tarde!", urlForm = url, scroll='inputURL') #volta ao index e escreve no text area

        else:

            return render_template('index.html', questionario = "Digite uma URL válida no campo acima!", scroll='inputURL') #volta ao index e escreve no text area



    if botaoForm == 'Recuperar Questões do Banco':
        #recupera questões aparir da url
        #se não estiver cadastrado emite um aviso de erro

        url = request.form['urlQuestionario'] #pega o valor do post (valor do textarea - name)

        #verifica se o campo url está vazio
        if len(url) > 0:

            records = buscaFomularioNoBanco(str(url)) #verifica se o form ja está cadastrado

            if len(records) > 0: #verifica se a url ja estava cadastrada

                questoes = ""

                #pega a resposta vinda do banco de separa os campos
                for row in records:
                    questoes = questoes + row[1]
                    idQuestionario = str(row[0])
                    urlQuestionario = row[2]

                questoes = json.loads(questoes) #deserializa os dados

                questoesTemp = ""

                #le cada uma das questões salvas no banco (não le o index 0 e nem o ultimo, que contem outroas informações)
                for n in range(1, len(questoes)- 1):
                    questoesTemp  = questoesTemp + questoes[n][0]['pergunta'] + "\n"


                return render_template('index.html', questionario = questoesTemp, urlForm = url, scroll='inputURL') #volta ao index e escreve no text area

            else:

                return render_template('index.html', questionario = "Esse fomulário ainda não foi cadastrado!", urlForm = url, scroll='inputURL') #volta ao index e escreve no text area

        else:

            return render_template('index.html', questionario = "Digite uma URL válida no campo acima!", scroll='inputURL') #volta ao index e escreve no text area


    ################################################### FERRAMENTAS ADM  ###################################################

    botaoADM = request.form.get("botaoADM") #captura o botão pressionado (o name do botao)


    #pega o click do botao Lista todos Usuários
    if botaoADM == 'Lista todos Usuários':

        records = buscaTodosUsuarios() #busca no banco todos os usuarios

        if len(records) > 0: #verifica se o banco retornou algum registro

            usuarios = ""

            #le cada um dos registros recebidos
            for row in records:
                usuarios = usuarios + "ID: " + str(row[0]) + " idUsuario: " + str(row[1]) + "\n"

            return render_template('index.html', textoADM = usuarios, scroll='inputADM') #volta ao index e escreve no text area

        else:

            return render_template('index.html', textoADM = "Não existem registros no banco!!!", scroll='inputADM') #volta ao index e escreve no text area


    #pega o click do botao Buscar Usuário pelo idUsuario
    if botaoADM == 'Buscar Usuário pelo idUsuario':
        #busca usuario pelo idUsuario

        id = request.form['formADM'] #pega o valor do post (valor do textarea - name)


        if len(id) > 0: #verifica se foi digitado algo no campo

            records = buscaidUsuario(str(id)) #busca o resgistro no banco pelo numero de telefone

            resposta = ""

            if len(records) > 0:  #verifica se o banco retornou algum registro

                for row in records:
                    resposta = resposta + "ID: " + str(row[0]) + ", idUsuario: " + str(row[1]) + "\n"
                    #resposta = resposta + str(row)

            else:

                resposta = "Não existem resgistros"

            return render_template('index.html', textoADM = resposta, scroll='inputADM') #volta ao index e escreve no text area

        else:

            return render_template('index.html', textoADM ="Digite o IdUsuario do usuário", scroll='inputADM') #volta ao index e escreve no text area



    #pega o click do botao Deletar Usuário pelo ID
    if botaoADM == 'Deletar Usuário pelo ID':
        #deleta um usuario pelo ID

        id = request.form['formADM'] #pega o valor do post (valor do textarea - name)

        if len(id) > 0: #verifica se foi digitado algo no campo

            records = deletaUsuarioPeloID(id) #deleta o usuario no banco (e pega o retorno)

            return render_template('index.html', textoADM = str(records) + " registro deletado\n ID = " + id, scroll='inputADM') #volta ao index e escreve no text area

        else:

            return render_template('index.html', textoADM ="Digite o ID do usuário", scroll='inputADM') #volta ao index e escreve no text area



    #pega o click do botao Deletar Tudo
    if botaoADM == 'Deletar Tudo':
    # Limpa os dados das duas tabelas

        url = request.form['urlQuestionario'] #pega o valor do post (valor do textarea - name)

        records = limpaTabelas() #limpa todas as tabelas do banco (usuarios e formularios)

        resposta = ""

        if records[0] == 1:
            resposta = resposta + "Registros da tabela formularios apagados\n"

        if records[1] == 1:
            resposta = resposta + "Registros da tabela usuários apagados"

        return render_template('index.html', textoADM = resposta, urlForm = url, scroll='inputADM') #volta ao index e escreve no text area


