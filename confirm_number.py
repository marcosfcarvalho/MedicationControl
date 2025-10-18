def confirma_int(numero): #essa função vai verificar se o usuario digitou um numero inteiro 
	while True:
		try:
			#variavel local que vai receber os valores inteiros
			return int(numero) # Não é preciso colocar um "break" pois o retorno da função vai encerrar o loop.
		
		except ValueError: #caso o programa dê erro ele entra nessa parte e força o usuario a digitar outra vez

			numero = (input("	Digite apenas números validos: ")) #aqui ele chama a função novamente, pedindo para o usuario digitar outro numero
		
		
		
def confirma_float(numero): #essa função vai verificar se o usuario digitou um numero float
	while True:
		try:
			#variavel local que vai receber os valores float
			numero = float(numero) # Tenta converter o input para float
			if (numero * 100)%25 == 0:
				return float(numero) # Não é preciso colocar um "break" pois o retorno da função vai encerrar o loop.
			else:
				numero = (input("	Digite apenas números validos: "))
			
		except ValueError: #caso o programa dê erro ele entra nessa parte e força o usuario a digitar outra vez
			numero = (input("	Digite apenas números validos: "))
