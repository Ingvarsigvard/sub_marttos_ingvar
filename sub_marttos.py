from datetime import datetime

# Estruturas de dados globais
alunos = {}  # Dicionário: id_aluno -> (nome, email)
cursos = {}  # Dicionário: id_curso -> {"nome": nome, "instrutor": instrutor, "tags": {}}
matriculas = {}  # Dicionário: id_curso -> set(id_aluno)
pilha_desfazer = []  # Pilha para desfazer ações (LIFO)

# Classe para vinculo da lista encadeada (Node)
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# Classe para lista encadeada (Fila FIFO para histórico)
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
        if self.size > 50:  # Limite de 50 registros no histórico
            self.pop_front()

    def pop_front(self):
        if self.head:
            self.head = self.head.next
            self.size -= 1
            if not self.head:  # Se a lista ficou vazia após remover o head
                self.tail = None

    def list_all(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

historico = LinkedList()  # Fila para histórico (máximo 50 registros) (FIFO)

# --- Funções de Gerenciamento ---

def gerar_proximo_id(dicionario_entidades):
    """Gera o próximo ID sequencial para um dicionário de entidades."""
    return max(dicionario_entidades.keys(), default=0) + 1

def registrar_acao(acao: str):
    """Registra uma ação no histórico com timestamp."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    historico.append(f"[{timestamp}] {acao}")

def cadastrar_aluno(nome: str, email: str):
    """Cadastra um novo aluno no sistema."""
    if not nome.strip() or not email.strip():
        print("Erro: Nome e e-mail do aluno não podem estar vazios.")
        return

    # Verifica se o e-mail já existe para evitar duplicidade
    for id_aluno, dados in alunos.items():
        if dados[1].lower() == email.strip().lower():
            print(f"Erro: Aluno com o e-mail '{email}' já cadastrado (ID: {id_aluno}).")
            return

    id_aluno = gerar_proximo_id(alunos)
    alunos[id_aluno] = (nome.strip(), email.strip())  # Armazena como tupla
    acao = f"Aluno '{nome.strip()}' cadastrado com ID {id_aluno}"
    print(f"Aluno '{nome.strip()}' cadastrado com sucesso. ID: {id_aluno}")
    registrar_acao(acao)
    pilha_desfazer.append({"tipo": "cadastro_aluno", "id_aluno": id_aluno})

def cadastrar_curso(nome: str, instrutor: str):
    """Cadastra um novo curso no sistema."""
    if not nome.strip() or not instrutor.strip():
        print("Erro: Nome do curso e instrutor não podem estar vazios.")
        return

    # Verifica se o curso já existe (pelo nome e instrutor)
    for id_curso, dados in cursos.items():
        if dados['nome'].lower() == nome.strip().lower() and \
           dados['instrutor'].lower() == instrutor.strip().lower():
            print(f"Erro: Curso '{nome.strip()}' com instrutor '{instrutor.strip()}' já cadastrado (ID: {id_curso}).")
            return

    id_curso = gerar_proximo_id(cursos)
    # Adicionando o campo 'tags' como um dicionário vazio
    cursos[id_curso] = {"nome": nome.strip(), "instrutor": instrutor.strip(), "tags": {}}
    acao = f"Curso '{nome.strip()}' cadastrado com ID {id_curso}"
    print(f"Curso '{nome.strip()}' cadastrado com sucesso. ID: {id_curso}")
    registrar_acao(acao)
    pilha_desfazer.append({"tipo": "cadastro_curso", "id_curso": id_curso})

# NOVA FUNÇÃO: Gerenciar Tags de Curso
def gerenciar_tags_curso(id_curso: int):
    """Permite adicionar ou remover tags de um curso."""
    if id_curso not in cursos:
        print(f"Erro: Curso com ID {id_curso} não encontrado.")
        return

    curso = cursos[id_curso]
    print(f"\n--- Gerenciando Tags para o Curso: {curso['nome']} (ID: {id_curso}) ---")
    print(f"Tags Atuais: {', '.join(curso['tags'].keys()) if curso['tags'] else 'Nenhuma'}")

    while True:
        print("\n1. Adicionar Tag")
        print("2. Remover Tag")
        print("0. Voltar ao Menu Principal")
        escolha = input("Escolha uma opção para tags: ").strip()

        if escolha == '1':
            tag = input("Digite a tag para adicionar: ").strip().lower()
            if tag:
                if tag not in curso['tags']:
                    curso['tags'][tag] = True # Usando um booleano simples como valor da tag
                    acao = f"Tag '{tag}' adicionada ao curso '{curso['nome']}' (ID: {id_curso})"
                    print(f"Tag '{tag}' adicionada com sucesso!")
                    registrar_acao(acao)
                    pilha_desfazer.append({"tipo": "adicionar_tag", "id_curso": id_curso, "tag": tag})
                else:
                    print(f"A tag '{tag}' já existe para este curso.")
            else:
                print("Tag não pode ser vazia.")
        elif escolha == '2':
            tag = input("Digite a tag para remover: ").strip().lower()
            if tag:
                if tag in curso['tags']:
                    del curso['tags'][tag]
                    acao = f"Tag '{tag}' removida do curso '{curso['nome']}' (ID: {id_curso})"
                    print(f"Tag '{tag}' removida com sucesso!")
                    registrar_acao(acao)
                    pilha_desfazer.append({"tipo": "remover_tag", "id_curso": id_curso, "tag": tag})
                else:
                    print(f"A tag '{tag}' não foi encontrada neste curso.")
            else:
                print("Tag não pode ser vazia.")
        elif escolha == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")

def matricular_aluno(nome_aluno: str, id_curso: int):
    """Matricula um aluno em um curso existente."""
    id_aluno = None
    for id_a, dados in alunos.items():
        if dados[0].lower() == nome_aluno.strip().lower():  # Busca por nome (case-insensitive)
            id_aluno = id_a
            break

    if id_aluno is None:
        print(f"Erro: Aluno '{nome_aluno.strip()}' não encontrado.")
        return

    if id_curso not in cursos:
        print(f"Erro: Curso com ID {id_curso} não encontrado.")
        return

    if id_curso not in matriculas:
        matriculas[id_curso] = set()  # Inicializa o set se o curso ainda não tiver matrículas

    if id_aluno not in matriculas[id_curso]:
        matriculas[id_curso].add(id_aluno)
        acao = f"Aluno '{alunos[id_aluno][0]}' matriculado no curso '{cursos[id_curso]['nome']}'"
        print(f"Aluno '{alunos[id_aluno][0]}' matriculado no curso '{cursos[id_curso]['nome']}'.")
        registrar_acao(acao)
        pilha_desfazer.append({"tipo": "matricula", "id_aluno": id_aluno, "id_curso": id_curso})
    else:
        print(f"Erro: Aluno '{alunos[id_aluno][0]}' já está matriculado neste curso.")

def cancelar_matricula(nome_aluno: str, id_curso: int):
    """Cancela a matrícula de um aluno em um curso."""
    id_aluno = None
    for id_a, dados in alunos.items():
        if dados[0].lower() == nome_aluno.strip().lower():
            id_aluno = id_a
            break

    if id_aluno is None:
        print(f"Erro: Aluno '{nome_aluno.strip()}' não encontrado.")
        return

    if id_curso not in cursos:
        print(f"Erro: Curso com ID {id_curso} não encontrado.")
        return

    if id_curso in matriculas and id_aluno in matriculas[id_curso]:
        matriculas[id_curso].discard(id_aluno)
        acao = f"Matrícula cancelada: Aluno '{alunos[id_aluno][0]}' no curso '{cursos[id_curso]['nome']}'"
        print("Matrícula cancelada com sucesso.")
        registrar_acao(acao)
        pilha_desfazer.append({"tipo": "cancelamento", "id_aluno": id_aluno, "id_curso": id_curso})
    else:
        print(f"Erro: Matrícula do aluno '{alunos[id_aluno][0]}' no curso '{cursos[id_curso]['nome']}' não encontrada.")

def desfazer_acao():
    """Desfaz a última ação registrada na pilha de desfazer."""
    if not pilha_desfazer:
        print("Nenhuma ação para desfazer.")
        return

    ultima_acao = pilha_desfazer.pop()
    tipo = ultima_acao["tipo"]

    if tipo == "matricula":
        id_aluno = ultima_acao["id_aluno"]
        id_curso = ultima_acao["id_curso"]

        if id_curso in matriculas and id_aluno in matriculas[id_curso]:
            matriculas[id_curso].discard(id_aluno)
            acao = f"Desfeito: Matrícula de '{alunos.get(id_aluno, ('Aluno Desconhecido',))[0]}' no curso '{cursos.get(id_curso, {}).get('nome', 'Curso Desconhecido')}' cancelada"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Matrícula não encontrada. Pode já ter sido desfeita ou não existia.")

    elif tipo == "cancelamento":
        id_aluno = ultima_acao["id_aluno"]
        id_curso = ultima_acao["id_curso"]

        if id_curso not in matriculas:
            matriculas[id_curso] = set() # Garante que o set exista se o curso ainda não tiver matrículas

        if id_aluno not in matriculas[id_curso]:
            matriculas[id_curso].add(id_aluno)
            acao = f"Desfeito: Matrícula de '{alunos.get(id_aluno, ('Aluno Desconhecido',))[0]}' no curso '{cursos.get(id_curso, {}).get('nome', 'Curso Desconhecido')}' restaurada"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Aluno já estava matriculado neste curso. Ação de cancelamento pode já ter sido desfeita.")

    elif tipo == "cadastro_aluno":
        id_aluno = ultima_acao["id_aluno"]
        if id_aluno in alunos:
            nome = alunos[id_aluno][0]
            del alunos[id_aluno]
            # Remove o aluno de todas as matrículas
            for alunos_ids_set in matriculas.values():
                alunos_ids_set.discard(id_aluno)
            acao = f"Desfeito: Cadastro do aluno '{nome}' removido"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Aluno não encontrado. Pode já ter sido removido.")

    elif tipo == "cadastro_curso":
        id_curso = ultima_acao["id_curso"]
        if id_curso in cursos:
            nome = cursos[id_curso]["nome"]
            del cursos[id_curso]
            matriculas.pop(id_curso, None) # Remove todas as matrículas relacionadas a este curso
            acao = f"Desfeito: Cadastro do curso '{nome}' removido"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Curso não encontrado. Pode já ter sido removido.")

    # NOVOS TIPOS DE DESFAZER PARA TAGS
    elif tipo == "adicionar_tag":
        id_curso = ultima_acao["id_curso"]
        tag = ultima_acao["tag"]
        if id_curso in cursos and tag in cursos[id_curso]['tags']:
            del cursos[id_curso]['tags'][tag]
            acao = f"Desfeito: Tag '{tag}' removida do curso '{cursos[id_curso]['nome']}'"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Tag ou curso não encontrados.")
    elif tipo == "remover_tag":
        id_curso = ultima_acao["id_curso"]
        tag = ultima_acao["tag"]
        if id_curso in cursos and tag not in cursos[id_curso]['tags']:
            cursos[id_curso]['tags'][tag] = True # Restaura a tag
            acao = f"Desfeito: Tag '{tag}' restaurada no curso '{cursos[id_curso]['nome']}'"
            print(acao)
            registrar_acao(acao)
        else:
            print("Erro ao desfazer: Curso não encontrado ou tag já existe.")


# --- Funções de Listagem ---

def listar_alunos():
    """Lista todos os alunos cadastrados."""
    if not alunos:
        print("Nenhum aluno cadastrado.")
    else:
        print("--- Alunos Cadastrados ---")
        for id_aluno, dados in alunos.items():
            print(f"ID: {id_aluno} | Nome: {dados[0]} | Email: {dados[1]}")

def listar_cursos():
    """Lista todos os cursos cadastrados."""
    if not cursos:
        print("Nenhum curso cadastrado.")
    else:
        print("--- Cursos Disponíveis ---")
        for id_curso, dados in cursos.items():
            tags_str = ', '.join(dados['tags'].keys()) if dados['tags'] else 'Nenhuma'
            print(f"ID: {id_curso} | Nome: {dados['nome']} | Instrutor: {dados['instrutor']} | Tags: {tags_str}")

def listar_matriculas_por_curso():
    """Lista as matrículas agrupadas por curso."""
    if not matriculas:
        print("Nenhuma matrícula realizada.")
    else:
        print("--- Matrículas por Curso ---")
        # Garante que os cursos sejam listados em ordem de ID
        for id_curso in sorted(matriculas.keys()):
            alunos_ids = matriculas[id_curso]
            curso = cursos.get(id_curso)
            if curso:
                print(f"\nCurso: {curso['nome']} (ID: {id_curso})")
                if alunos_ids:
                    # Ordena os alunos por ID para uma listagem consistente
                    for id_aluno in sorted(list(alunos_ids)):
                        aluno = alunos.get(id_aluno)
                        if aluno:
                            print(f"- {aluno[0]} (ID: {id_aluno})")
                        else:
                            print(f"- Aluno de ID {id_aluno} (removido)")
                else:
                    print("- Nenhum aluno matriculado neste curso.")
            else:
                print(f"\nErro: Curso com ID {id_curso} não encontrado (pode ter sido removido).")

def listar_historico():
    """Exibe o histórico de ações do sistema."""
    print("\n--- HISTÓRICO DE AÇÕES ---")
    registros = historico.list_all()
    if not registros:
        print("Nenhum registro no histórico.")
    else:
        for registro in registros:
            print(registro)

# --- Menu Principal ---

def menu():
    """Exibe o menu principal do sistema e gerencia as opções do usuário."""
    while True:
        print("\n=== SISTEMA DE GERENCIAMENTO DE CURSOS ===")
        print("1. Cadastrar aluno")
        print("2. Cadastrar curso")
        print("3. Matricular aluno em curso")
        print("4. Cancelar matrícula")
        print("5. Gerenciar tags de curso") # NOVA OPÇÃO NO MENU
        print("6. Listar alunos")
        print("7. Listar cursos")
        print("8. Listar matrículas por curso")
        print("9. Listar histórico de ações")
        print("10. Desfazer última ação")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip() # Remove espaços em branco da entrada

        if opcao == "1":
            nome = input("Nome do aluno: ").strip()
            email = input("Email do aluno: ").strip()
            cadastrar_aluno(nome, email)
        elif opcao == "2":
            nome = input("Nome do curso: ").strip()
            instrutor = input("Nome do instrutor: ").strip()
            cadastrar_curso(nome, instrutor)
        elif opcao == "3":
            listar_cursos() # Ajuda o usuário a escolher um curso existente
            nome_aluno = input("Nome do aluno: ").strip()
            try:
                id_curso = int(input("ID do curso para matricular: "))
                matricular_aluno(nome_aluno, id_curso)
            except ValueError:
                print("Entrada inválida: O ID do curso deve ser um número inteiro.")
        elif opcao == "4":
            nome_aluno = input("Nome do aluno: ").strip()
            try:
                id_curso = int(input("ID do curso para cancelar matrícula: "))
                cancelar_matricula(nome_aluno, id_curso)
            except ValueError:
                print("Entrada inválida: O ID do curso deve ser um número inteiro.")
        elif opcao == "5": # NOVA OPÇÃO DO MENU
            listar_cursos()
            try:
                id_curso = int(input("ID do curso para gerenciar tags: "))
                gerenciar_tags_curso(id_curso)
            except ValueError:
                print("Entrada inválida: O ID do curso deve ser um número inteiro.")
        elif opcao == "6": # Opção reindexada
            listar_alunos()
        elif opcao == "7": # Opção reindexada
            listar_cursos()
        elif opcao == "8": # Opção reindexada
            listar_matriculas_por_curso()
        elif opcao == "9": # Opção reindexada
            listar_historico()
        elif opcao == "10": # Opção reindexada
            desfazer_acao()
        elif opcao == "0":
            print("Encerrando o sistema. Até mais!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida do menu.")

# Inicia o menu principal
if __name__ == "__main__":
    menu()