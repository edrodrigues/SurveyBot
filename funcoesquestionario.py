import urllib.request #usado para fazer as requisições
import requests #usado para fazer as requisições


#função resposavel por receber a URL analisar o questionario e extrair questoes, alternativas, titulo do form, descrição do form e msg final
def extraiQuestoes(url):

    #verifica se a url está ok (busca por palavras chaves da url)
    if url.find("google") == -1 or url.find("forms") == -1:
        return False


    fp = urllib.request.urlopen(url)
    html = fp.read() #le o retorno da requisiçã como bytearray

    #converte o bytearray para uft8
    html = html.decode("utf8")

    #fecha a conexão
    fp.close()


    #verifica se a resposta html tem a palavra abaixo (verifica se é a resposta contém um form)
    if html.find("FB_PUBLIC_LOAD_DATA_ = ") == -1:
        return False


    #pega as questões do formulario (o separador será FB_PUBLIC_LOAD_DATA_ = )
    #-1 pega a ultima parte do texto, ou seja, após o separador "FB_PUBLIC_LOAD_DATA_ = "
    questoesRaw = html.split("FB_PUBLIC_LOAD_DATA_ = ",1)[-1]



    #remove o resto do html
    #0 pega a primeira parte do texto, ou seja, tudo antes de ",/forms" (deixa apenas o javascript)
    questoesRaw = questoesRaw.split("/forms",1)[0]



    nAux = "" #armazena o caracter anterior


    questionarioDic = {} #dicionario onde sera amarzenado toda a estrutura do questionario
    questionarioLista = [] #lista que armazena toda a estrutura do questionario (talvez seja mais facil de usar)

    contColcheteInicio = 0 #variavel de controle de contagem e sincronia com o texto

    stringTexto = False #usada pra diferenciar , (virgulas) de separação e , (virgulas) de string (que estão entre " ")
    stringVirgula = "," #controla a contagem de virguras de separação de campos

    contPergunta = 0 #variavel de controle de contagem e sincronia com o texto
    contResposta = 0 #variavel de controle de contagem e sincronia com o texto

    tituloForm = ""
    descricaoForm = ""
    msgFinal = ""

    auxFim = 3 #indetifica a posição do titulo do form

    contFim = 0 #usado para pegar as ultimas informações (titulo e descrição do form)
    fimDescricao = 0 # marca o fim da descrição do form

    idPergunta = "" #guarda o id da pergunta
    pergunta = "" #guarda o enuciado da pergunta
    tipoPergunta = "" #identifica o tipo de pergunta [1 a 10]
    respObrigatoria = "" #Se 1 indica obrigatoriedade de resposta para pergunta

    idResposta = "" #id da resposta (usado pra fazer o post com a resposta)
    tipoResposta = "" #indica o tipo de resposta (0 indica opção de marcar - 1 indica questão aberta para escrita de texto)
    atlNativ = "" #pega as alternativas de resposta
    alternativas = [] #lista que de alternativas de resposta

    notas = [] #usada para amazenar as notas das questões do tipo 5 (as duas ultimas posições guarda os conceitos [Bom,Ruim]) (usada tb para armazenar as questões do tipo 7)
    nota = "]" #usada para controlar as notas que serão salvas em questões do tipo 5

    flagGrade = False

    flagFim = False #usado para indetificar se as alternativas acabaram


    flagImagem = False #se true indica q ha figura na alternativa de resposta (não usado na primeira versão)
    idImagem = "" #id da imagem no html (não usado na primeira versão)

    subVirgula = 0 #conta as virgulas para separar os campos  (virgulas entre " " não são contadas - entende-se q faz parte do texto)


    for n in questoesRaw:
      if n == '[':
        contColcheteInicio = contColcheteInicio + 1

      if contColcheteInicio == 2 and n == "\"":
        fimDescricao = fimDescricao + 1

      if contColcheteInicio == 2 and n !="," and n!="\"" and n != '[' and n != ']' and n != '\n' and fimDescricao < 2: #pega a descrição do form
        descricaoForm = descricaoForm + n


      if contColcheteInicio >=3: #conta 3 colchetes para sincronizar

        if n != "[" and n != "," and contPergunta == 0:
          idPergunta = idPergunta + n #pega o id da pergunta

          if ord(n) < 48 or ord(n) > 57: #indica fim de questionario
            #print("FIM" + n + nAux)
            contPergunta = 99999 #muda os valores das varaiveis para pegar as ultimas informações
            contResposta = 0


        if  n == "\"" and nAux != "\\" : # se n == " (stringTexto = True indica quando uma string entre " " está sendo lida)
          if stringTexto == False:
            stringTexto = True
            stringVirgula = ""
          else:
            stringTexto = False
            stringVirgula = ","

        if n == "," and stringTexto == False: # incrementa caso n == , (conta as vírgulas que separa os campos, menos as virgulas de strings)
          contPergunta = contPergunta + 1
          contResposta = contResposta + 1

        if n != "\"" and n != stringVirgula and contPergunta == 1:
        #if n != "\"" and n != "," and contPergunta == 1: # 34 != ord(n) é o mesmo que n != "
          pergunta = pergunta + n

        if n != "," and contPergunta == 3 :
          tipoPergunta = tipoPergunta + n


        #pega o id da pergunta (para chegar aqui contPergunta contou 4 virgulas)
        if n != "[" and n != "," and contPergunta == 4:
          #print(colchete)
          idResposta = idResposta + n


        #trata as alternartivas para peguntas do tipo 0 e 1 (verificar se não tira outros campos de sincronia)

        if tipoPergunta == '0' or tipoPergunta == '1':
          #print(idPergunta, pergunta, tipoPergunta, idResposta, [atlNativ,tipoResposta, idImagem], contResposta)

          if n == '1' or n == '0':
            respObrigatoria = respObrigatoria + n


          #Verifica se chegou ao fim da questão (apos pegar todas as informações)
          if n == "]":
            subVirgula = subVirgula + 1
          elif n != "]" and n != "\n":
            subVirgula = 0


          #if subVirgula >= 4:
          if subVirgula >= 3:
            #reinicia a contagem

            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria": respObrigatoria[-1], "idResposta": idResposta}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria": respObrigatoria[-1], "idResposta": idResposta}])


            subVirgula = 0

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 0 e 1


        #trata as alternartivas para peguntas do tipo 2 3 e 4 (observar o 3)

        if tipoPergunta == '2' or tipoPergunta == '3' or tipoPergunta == '4':

          if n != "[" and n != "]" and n != "\"" and n != "," and n != "\n" and n != "]" and n != "" and contResposta == 5:
            atlNativ = atlNativ + n

          #usado para algunas variações do tipoPergunta == 3 pode ser (,["alternativa",null,null,null,0]) ou pode ser(,["alternativa"])
          if n == "[" and nAux == "," and contResposta == 6:
          #if contResposta == 6: ADMINISTRAÇÃO , [
            contResposta = 10
            #print("Teste: " + atlNativ, nAux, n)


          if n != "," and n != "\n" and n != "]" and flagFim == False and contResposta == 9:
            tipoResposta = tipoResposta + n


          if contResposta == 10:
            alternativas.append([atlNativ,tipoResposta, idImagem]) #guarda a alternativas e alguns valores na lista

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False
            contResposta = 5

          if n == "]":
            subVirgula = subVirgula + 1
          elif n != "\n" and n != "]":
            subVirgula = 0
            #respObrigatoria = ""

          if subVirgula == 2:
            flagFim = True


          if flagFim == True and n != "\n":
            respObrigatoria = respObrigatoria + n


          if subVirgula >= 3:
            #reinicia a contagem

            if len(alternativas) > 0:
              alternativas.pop() #remove o o ultimo elemento das alternativas


            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria": respObrigatoria[2], "idResposta": idResposta, "alternativas": alternativas[0:]}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria": respObrigatoria[2], "idResposta": idResposta, "alternativas": alternativas[0:]}])

            subVirgula = 0

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            flagFim = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2
            #break


        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 2, 3 e 4


        #trata as alternartivas para peguntas do tipo 5
        if tipoPergunta == '5':

          if n != "[" and n != "]" and n != "\"" and n != "," and n != "\n" and contPergunta >= 5:
            atlNativ = atlNativ + n


          if n == nota and atlNativ != "" : #salva as alternativas numa lista até q se enconte o fim das alternativas (salva na lista do n == ])
            notas.append(atlNativ)
            atlNativ = ""


          if n == "]": #indefifica o fim das alternativas e o fim da questão
            subVirgula = subVirgula + 1

          elif n != "]" and n != "\n": #zera o contador caso não seja o fim das alternativas
            subVirgula = 0
            respObrigatoria = ""

          if subVirgula == 2: #indefifica o fim das alternativas
            nota = "\""

          if subVirgula >= 3:
            #reinicia a contagem

            respObrigatoria = notas[-3]
            notas.pop(-3) #removeo o antipenultimo elemento das alternativas evita dois campos com o mesmo valor (remove bug)

            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria, "idResposta": idResposta, "alternativas": notas[0:]}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria, "idResposta": idResposta, "alternativas": notas[0:]}])


            subVirgula = 0

            nota = "]"
            notas.clear()

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 5

        #trata as alternartivas para peguntas do tipo 6 e 8
        if tipoPergunta == '6' or tipoPergunta == '8':

          if contPergunta >= 3: #indefifica o fim das alternativas e o fim da questão

            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta}])


            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 6 e 8

        #trata as alternartivas para peguntas do tipo 7
        if tipoPergunta == '7':

           #pega o id da resposta
          if contResposta == 4 and flagGrade == False:
            if n != "[" and n != "]" and n !="\"" and n !="\n" and n !="," and flagGrade == False:
              atlNativ = atlNativ + n

          #salva o id da resposta
          if n == "," and n != "" and len(atlNativ) > 0 and flagGrade == False:
            idResposta = atlNativ
            notas.append(idResposta)
            #print(idPergunta, pergunta, tipoPergunta, notas)
            atlNativ = ""


          #pega as opções de resposta
          if contResposta >= 5 and flagGrade == False:

            #pega letra por letra da alternativa
            if n != "[" and n != "]" and n != "\"" and n != "\n" and n != ",":
              atlNativ = atlNativ + n


            #salva a alternativa (coluna)
            if n == "]" and len(atlNativ) > 0:
              notas.append(atlNativ)
              #print(notas)
              atlNativ = ""


            #se pegou todas as alternativas
            if subVirgula == 2:
              flagGrade = True
              contResposta = 0
              atlNativ = ""


          #verifica se a resposta é obrigatoria
          if contResposta == 1 and flagGrade == True:
            if n !=",":
              respObrigatoria = n
              notas.append(respObrigatoria)

          #pega a opção da linha
          if contResposta == 2 and flagGrade == True:
            #pega letra por letra da alternativa
            if n != "[" and n != "]" and n != "\"" and n != "\n" and n != ",":
              atlNativ = atlNativ + n


            #salva a alternativa
            if n == "]" and len(atlNativ) > 0:
              notas.append(atlNativ)
              #print(notas)
              atlNativ = ""


          if contResposta == 10 and flagGrade == True:
            #pega o tipo de gradForm
            if n != "[" and n != "]" and n != "\"" and n != "\n" and n != ",":
              atlNativ = atlNativ + n


            #salva a alternativa
            if n == "]" and len(atlNativ) > 0:
              notas.append(atlNativ)
              #print(notas)
              atlNativ = ""

              alternativas.append(notas[:]) #copia notas para alternartivas

              notas.clear()
              contResposta = 3
              flagGrade = False


          if n == "]":
            subVirgula = subVirgula + 1

          if n != "]" and n != "\n":
            subVirgula = 0

          if subVirgula >= 3:


            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "alternativas": alternativas[0:]}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "alternativas": alternativas[0:]}])


            subVirgula = 0

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            flagGrade = False

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 7


        #trata as alternartivas para peguntas do tipo 9 e 10
        if tipoPergunta == '9' or tipoPergunta == '10':

          if n != "," and contPergunta == 6:
            respObrigatoria = respObrigatoria + n;

          if n == "]" and n != "\n":
            subVirgula = subVirgula + 1


          if subVirgula >= 3:


            if tipoPergunta == '9':
              questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria, "idResposta": idResposta}
              questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria, "idResposta": idResposta}])

            else:
              questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria[1], "idResposta": idResposta}
              questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta, "respObrigatoria":respObrigatoria[1], "idResposta": idResposta}])


            subVirgula = 0

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 9 e 10


        #trata as alternartivas para peguntas do tipo 11
        if tipoPergunta == '11':

          if n == "]" and n != "\n":
            subVirgula = subVirgula + 1


          if subVirgula >= 3:

            questionarioDic[idPergunta] = {"pergunta": pergunta,"tipoPergunta": tipoPergunta}
            questionarioLista.append([{"pergunta": pergunta,"tipoPergunta": tipoPergunta}])


            subVirgula = 0

            atlNativ = ""
            tipoResposta = ""
            idImagem = ""
            flagImagem = False

            alternativas.clear()

            idPergunta = ""
            pergunta = ""
            tipoPergunta = ""
            idResposta = ""
            respObrigatoria = ""

            contPergunta = 0
            contResposta = 0
            contColcheteInicio = 2

        # FIM DO TRATAMENTO DE PEGUNTAS DO TIPO 11

        # PEGA AS ULTIMAS INFORMAÇOES (TITULO DO FORM E MSG FINAL)
        if contPergunta >= 99999:
          #print(contFim, n)
          if n == "\"":
            contFim = contFim + 1

          #verifica a posição do titulo do form
          if contResposta == 12 and n == "\"":
            auxFim = 7 #essa variavel é inicializada com 3

          if contFim == 1 and n != "\"":
            msgFinal = msgFinal + n


          if contFim == auxFim and n != "\"":
            tituloForm = tituloForm + n



      nAux = n # nAux usado no caso de caracter especuiais como \" \\ (evita bug - finalizar a leitura de um no ponto)



    #adiciona ao fim No dicionario o titulo a descrição e a msg final
    questionarioDic['Form'] = {'tituloForm': tituloForm, 'descricaoForm':descricaoForm, 'msgFinal': msgFinal}

    #questionarioLista.insert(0, [{'tituloForm': tituloForm, 'descricaoForm':descricaoForm, 'msgFinal': msgFinal}]) #insere as infomações sobre o form na posição 0
    questionarioLista.insert(0, [{'tituloForm': tituloForm, 'descricaoForm':descricaoForm}]) #insere as infomações sobre o form na posição 0
    questionarioLista.append([{'msgFinal': msgFinal, 'url': url}]) #insere a msg de agradecimento final no fim da lista e a URL do form


    # AO FINAL ESSE CODIGO GERA DUAS SAIDAS UM DICIONARIO E UMA LISTA DE DICIONARIOS
    # NO DICIONARIO AS ALTERNATIVAS SÃO GUARDADAS NUMA LISTA DE LISTAS
    # NA LISTA AS PEGUNTAS ESTÃO EM ORDEM

    return questionarioLista



#recebe a pergunta (uma lista), analisa o tipo de pergunta e devolte o texto formatado para o whatsapp
def formataMsgPergunta(questoesLista):

    msg = ""

    #Trata questões com entrada para escrita de texto
    if questoesLista[0][0]['tipoPergunta'] == '0' or questoesLista[0][0]['tipoPergunta'] == '1':
        msg = "*" + questoesLista[0][0]['pergunta'] + "*"


    #Trata questoes de multipla escolha e lista suspensa
    if questoesLista[0][0]['tipoPergunta'] == '2' or questoesLista[0][0]['tipoPergunta'] == '3' or questoesLista[0][0]['tipoPergunta'] == '4':
        msg = "*" + questoesLista[0][0]['pergunta'] + "*" + "\n_(Digite apenas a b c...)_\n\n"
        #pega as alternativas
        for n in range(0, len(questoesLista[0][0]['alternativas'])):
            msg = msg + "*" + chr(65 + n) + ")* " + questoesLista[0][0]['alternativas'][n][0] + "\n" #pega o texto da alternativa e gera as altenativas para whatsapp


    #Trata de questões do tipo escala linear (questão para escolher uma nota)
    if questoesLista[0][0]['tipoPergunta'] == '5':
        msg = "*" + questoesLista[0][0]['pergunta'] + "*"
        msg = msg + "\n_Digite uma nota de " + questoesLista[0][0]['alternativas'][0] + " (" + questoesLista[0][0]['alternativas'][-2] + ") a " + questoesLista[0][0]['alternativas'][-3] + " (" + questoesLista[0][0]['alternativas'][-1] + ")_\n\n"

    #Trata Titulos, Seções e quadro com fotos
    if questoesLista[0][0]['tipoPergunta'] == '6' or questoesLista[0][0]['tipoPergunta'] == '8' or questoesLista[0][0]['tipoPergunta'] == '11':
        msg = "*" + questoesLista[0][0]['pergunta'] + "*"

    return msg


#recebe a pergunta (uma lista), analisa o tipo de pergunta e devolte o texto formatado para o whatsapp
def verificaResposta(questoesLista, respostasLista, msgRec):

    #Trata a respostas questões com entrada para escrita de texto
    if questoesLista[0][0]['tipoPergunta'] == '0' or questoesLista[0][0]['tipoPergunta'] == '1':
        if len(msgRec) <= 3:
            #se o texto for muito curto, retorna esse erro
            return [False,"_Texto muito curto, por favor, escreva um pouco mais_"]

        else:
            #monta a resposta (dicionario com a resposta)
            chave = "entry." + str(questoesLista[0][0]['idResposta'])
            respostasLista[chave] = msgRec
            return [True,respostasLista]


     #Trata a resposta de questoes de multipla escolha e lista suspensa
    if questoesLista[0][0]['tipoPergunta'] == '2' or questoesLista[0][0]['tipoPergunta'] == '3' or questoesLista[0][0]['tipoPergunta'] == '4':
        if len(msgRec) == 1 and msgRec.isalpha():

            msgRec = msgRec.lower() #converte a letra recebida para minuscula

            if (ord(msgRec) - 97) < len(questoesLista[0][0]['alternativas']):

                opc = (ord(msgRec) - 97) #converte a letra para numero

                #monta a resposta (dicionario com a resposta)
                chave = "entry." + str(questoesLista[0][0]['idResposta'])
                respostasLista[chave] = str(questoesLista[0][0]['alternativas'][opc][0])
                return [True,respostasLista]
            else:
                return [False, "_Essa alternativa não existe, digite apenas a b ou c..._"]
        else:
            return [False, "_Por favor digite apenas a letra da alternativa, a b ou c..._"]



    #Trata a resposta de questões do tipo escala linear (questão para escolher uma nota)
    if questoesLista[0][0]['tipoPergunta'] == '5':

        contChar = 1 #usado para idetificar a quantidade de digitos da nota

        #testa se existe apenas numeros na resposta
        if msgRec.isdigit():

            #ajusta a variavel para notas com dois digitos
            if questoesLista[0][0]['alternativas'][-3] == "10":
                contChar = 2

            if len(msgRec) <= contChar and int(msgRec) >= int(questoesLista[0][0]['alternativas'][0]) and int(msgRec) <= int(questoesLista[0][0]['alternativas'][-3]):

                #monta a resposta (dicionario com a resposta)
                chave = "entry." + str(questoesLista[0][0]['idResposta'])
                respostasLista[chave] = str(msgRec)
                return [True,respostasLista]

            else:
                return [False, "_A nota deve ser de " + questoesLista[0][0]['alternativas'][0] + " a " + questoesLista[0][0]['alternativas'][-3] + "_\n\n"]

        else:
            return [False, "_Digite apenas números!_"]



#envia resposta para google forms
def enviaResposta(url,respostasLista):

    # FAZ O POST COM AS RESPOSTAS PARA UM GOOGLE FORM
    # Ex de url
    # url = 'https://docs.google.com/forms/d/e/1FAIpQLSff7W2kCDkgYzoeaYIolFN9vf8X4dmBK-S60bLIeaZBaNosDA/formResponse'

    #ajusta a url (troca viewform por formResponse)
    url = url.replace("viewform", "formResponse")

    #return url

    form_data = respostasLista

    form_data['draftResponse'] = []
    form_data['pageHistory'] = 0


    user_agent = {'Referer': url,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(url, data=form_data, headers=user_agent)

    #return r

