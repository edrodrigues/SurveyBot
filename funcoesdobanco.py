# Funçoes destinadas a se comunicar com o banco de dados
# A virgula ao sim da query sql não é obrigatória


import mysql.connector #usado para se conectar com o banco de dados
import json


#dados para comunicação com o banco
def conexao():

    connection = mysql.connector.connect(
      host="jonatascoelho.mysql.pythonanywhere-services.com",
      user="jonatascoelho",
      database="jonatascoelho$flowbot",
      password="YtH3t@ck3KFvY@7"
    )

    return connection


#usado apra fechar a conexão com o banco ao fim de cada operação
def fechaConexao(connection, cursor):

    #fecha a conexão com o banco
    if (connection.is_connected()):
        connection.close()
        cursor.close()



#busca por registros de usuarios no banco (busca por idUsuario)
def buscaTodosUsuarios():

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "SELECT * FROM usuarios";

    cursor = connection.cursor()
    cursor.execute(sql)

    records = cursor.fetchall()


    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return records


#busca por registros de usuarios no banco (busca por idUsuario)
def buscaidUsuario(id):

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "SELECT * FROM usuarios WHERE idUsuario = '" + id + "'"


    cursor = connection.cursor()
    cursor.execute(sql)

    records = cursor.fetchall()


    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return records



#salva um novo usuario no banco (salva pelo idUsuario - numero de telefone no padrão whatsapp:+5588987654321)
def salvaidUsuarioNoBanco(id):

    connection = conexao() #pega os dados apra a conexão com o banco

    #sql = "INSERT INTO usuarios (respostas, perguntas) VALUES ('teste', 'teste2')"
    #sql = "INSERT INTO usuarios (idUsuario) VALUES ('" + id + "')"

    respostas = {} #cria um dicionario vazio
    respostasLista = json.dumps(respostas) #serializa os dados pra salvar no banco

    sql = "INSERT INTO usuarios (idUsuario, respostas) VALUES ('" + id + "','" + respostasLista + "')"

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados



#usado para atualizar as peguntas no registro do usuario (insere novas perguntas ou edita as existentes)
def atualizaPerguntasUsuario(id, perguntas):

    connection = conexao() #pega os dados para a conexão com o banco

    #sql = "UPDATE usuarios SET perguntas = %s WHERE idUsuario = %s"

    cursor = connection.cursor()
    cursor.execute("UPDATE usuarios SET perguntas = %s WHERE idUsuario = %s", (perguntas,id))
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados


#usado para atualizar as peguntas no registro do usuario (insere novas perguntas ou edita as existentes)
def atualizaRespostasUsuario(id, respostas):

    connection = conexao() #pega os dados para a conexão com o banco

    #sql = "UPDATE usuarios SET perguntas = %s WHERE idUsuario = %s"

    cursor = connection.cursor()
    cursor.execute("UPDATE usuarios SET respostas = %s WHERE idUsuario = %s", (respostas,id))
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados


#deleta um registrdo da tabela de usuarios (usa o idUsuario para deletar)
def deletaPoridUsuario(id):

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "DELETE FROM usuarios WHERE idUsuario = " + id;

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados



#salva um formulario na tabela formularios (salva a url e as perguntas)
def salvafomularioNoBanco(url, perguntas):


    connection = conexao() #pega os dados apra a conexão com o banco

    cursor = connection.cursor()

    cursor.execute("INSERT INTO formularios (url, perguntas) VALUES (%s, %s)", (url,perguntas))

    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados



#busca um ou todos os formularios na tabela formularios (se url == False busca todos)
def buscaFomularioNoBanco(url):

    connection = conexao() #pega os dados para a conexão com o banco

    if url == False:
        sql = "SELECT * FROM formularios"
    else:
        sql = "SELECT * FROM formularios WHERE url = '" + url +"'"

    cursor = connection.cursor()
    cursor.execute(sql)

    records = cursor.fetchall()


    #fecha a conexão com o banco
    #fechaConexao(connection, cursor)

    return records


#atualiza um formulario na tabela formularios (salva a url e as perguntas)
def atualizaFomularioNoBanco(url, perguntas):

    connection = conexao() #pega os dados para a conexão com o banco

    #sql = "UPDATE formularios SET perguntas = '" + pickle.dumps(perguntas) + "' WHERE url = '" + url + "'"

    cursor = connection.cursor()
    #cursor.execute(sql)
    cursor.execute("""UPDATE formularios SET perguntas = (%s) WHERE url = (%s)""", (perguntas, url))
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados


#Limpa todas as tabelas do banco (deleta tudo)
def limpaTabelas():

    connection = conexao() #pega os dados para a conexão com o banco

    #deleta todos os registros da tabela formularios
    sql = "DELETE FROM formularios"

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

    formFlag = cursor.rowcount


    #deleta todos os registros da tabela usuarios
    sql = "DELETE FROM usuarios"

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()


    usuarFlag = cursor.rowcount

    fechaConexao(connection, cursor)


    return [formFlag,usuarFlag] #retorna uma lista com a respota da execução de cada query



#busca por registros de usuarios no banco pelo ID (chave primaria) (VERIFICAR NECESSIDADE DESSA FUNÇÃO)
def buscaID(id):

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "SELECT * FROM usuarios WHERE ID = " + id;
    #sql = "SELECT * FROM usuarios";
    #sql = "SELECT * FROM usuarios WHERE respostas = '" + id + "'";#


    cursor = connection.cursor()
    cursor.execute(sql)

    records = cursor.fetchall()


    #fecha a conexão com o banco
    #fechaConexao(connection, cursor)

    return records



#deleta um usuario pelo seu ID
def deletaUsuarioPeloID(id):

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "DELETE FROM usuarios WHERE ID = " + id;

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados


#deleta um usuario pelo seu idUsuario
def deletaUsuarioPeloidUsuario(id):

    connection = conexao() #pega os dados para a conexão com o banco

    sql = "DELETE FROM usuarios WHERE idUsuario = '" + id + "'";

    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

    cursorTemp = cursor.rowcount

    #fecha a conexão com o banco
    fechaConexao(connection, cursor)

    return cursorTemp #retorna o numero de registros afetados

