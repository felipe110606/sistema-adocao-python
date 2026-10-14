animais = []




def mostrar_menu():
    print("=== SISTEMA DE ADOÇÃO ===")
    print("1 - Listar Animais")
    print("2 - Cadastrar Animais")
    print("3 - Buscar Animais")
    print("4 - Marcar Animal como Adotado")
    print("5 - Excluir Animal")
    print("6 - Editar Animal")
    print("7 - Sair")




def listar_animais(animais):
    if not animais:
        print("Nenhum animal cadastrado.")
    else:
        print("=== ANIMAIS CADASTRADOS ===")


        for animal in animais:
            print(f"Nome: {animal['nome']}")
            print(f"Espécie: {animal['especie']}")
            print(f"Idade: {animal['idade']}")
            print(f"Porte: {animal['porte']}")
            print(f"Status: {animal['status']}")
            print("--------------------")




def cadastrar_animal(animais):
    nome = input("Nome do animal: ")
    especie = input("Espécie do animal: ")


    while True:
        try:
            idade = int(input("Idade do animal: "))


            if idade >= 0:
                break
            else:
                print("A idade não pode ser negativa.")


        except ValueError:
            print("Digite uma idade válida.")


    porte = input("Porte do animal: ")


    animal = {
        "nome": nome,
        "especie": especie,
        "idade": idade,
        "porte": porte,
        "status": "Disponível"
    }


    animais.append(animal)


    print("Animal cadastrado com sucesso!")




def buscar_animal(animais):
    nome = input(
        "Digite o nome do animal que deseja buscar: "
    ).strip().lower()


    encontrado = False


    for animal in animais:
        if animal["nome"].strip().lower() == nome:
            print("Animal encontrado!")
            print(f"Nome: {animal['nome']}")
            print(f"Espécie: {animal['especie']}")
            print(f"Idade: {animal['idade']}")
            print(f"Porte: {animal['porte']}")
            print(f"Status: {animal['status']}")


            encontrado = True
            break


    if not encontrado:
        print("Animal não encontrado.")




def marcar_como_adotado(animais):
    nome = input("Digite o nome do animal: ").strip().lower()


    encontrado = False


    for animal in animais:
        if animal["nome"].strip().lower() == nome:
            animal["status"] = "Adotado"


            print("Animal marcado como adotado!")


            encontrado = True
            break


    if not encontrado:
        print("Animal não encontrado.")




def excluir_animal(animais):
    nome = input(
        "Digite o nome do animal que deseja excluir: "
    ).strip().lower()


    encontrado = False


    for animal in animais:
        if animal["nome"].strip().lower() == nome:
            animais.remove(animal)


            print("Animal excluído com sucesso!")


            encontrado = True
            break


    if not encontrado:
        print("Animal não encontrado.")




def editar_animal(animais):
    nome = input(
        "Digite o nome do animal que deseja editar: "
    ).strip().lower()


    encontrado = False


    for animal in animais:
        if animal["nome"].strip().lower() == nome:


            novo_nome = input("Novo nome: ")
            nova_especie = input("Nova espécie: ")


            while True:
                try:
                    nova_idade = int(input("Nova idade: "))


                    if nova_idade >= 0:
                        break
                    else:
                        print("A idade não pode ser negativa.")


                except ValueError:
                    print("Digite uma idade válida.")


            novo_porte = input("Novo porte: ")


            animal["nome"] = novo_nome
            animal["especie"] = nova_especie
            animal["idade"] = nova_idade
            animal["porte"] = novo_porte


            print("Animal atualizado com sucesso!")


            encontrado = True
            break


    if not encontrado:
        print("Animal não encontrado.")




while True:
    mostrar_menu()


    opcao = input("Escolha uma opção: ")


    if opcao == "1":
        listar_animais(animais)


    elif opcao == "2":
        cadastrar_animal(animais)


    elif opcao == "3":
        buscar_animal(animais)


    elif opcao == "4":
        marcar_como_adotado(animais)


    elif opcao == "5":
        excluir_animal(animais)


    elif opcao == "6":
        editar_animal(animais)


    elif opcao == "7":
        print("Saindo do programa...")
        break


    else:
        print("Opção inválida.")

