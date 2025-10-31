import math
import random
import re

#region ==================== PARTE 1: CONVERSÃO BINÁRIO PARA TEXTO ====================
def binario_para_texto(texto_binario):
    texto_convertido = ""
    grupos_binarios = texto_binario.strip().split()
    
    for grupo in grupos_binarios:
        # Converte binário para número
        numero = int(grupo, 2)
        # Converte número para letra
        letra = chr(numero)
        texto_convertido += letra
    
    return texto_convertido
#endregion

#region ==================== PARTE 2: CIFRA DE CÉSAR ====================
def decifrar_cesar(texto_cifrado, deslocamento):
    """
    Cada letra é movida x posições no alfabeto 
    PS: x = atributo deslocamento
    """
    texto_decifrado = ""
    
    for letra in texto_cifrado:
        if letra.isalpha():
            # Decide se é maiúscula ou minúscula
            base = 'A' if letra.isupper() else 'a'
            # Calcula nova posição da letra
            pos_original = ord(letra) - ord(base)
            pos_nova = (pos_original - deslocamento) % 26
            letra_nova = chr(pos_nova + ord(base))
            texto_decifrado += letra_nova
        else:
            texto_decifrado += letra
    
    return texto_decifrado

def quebrar_cesar(texto_cifrado, analisador):
    """
    Tenta todos os deslocamentos possíveis (0-25) para quebrar a Cifra de César
    """
    melhor_deslocamento = 0
    melhor_pontuacao = -999999
    melhor_texto = ""
    
    for deslocamento in range(26):
        texto_teste = decifrar_cesar(texto_cifrado, deslocamento)
        pontuacao = analisador.calcular_pontuacao(texto_teste)
        
        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_deslocamento = deslocamento
            melhor_texto = texto_teste
    
    return melhor_deslocamento, melhor_texto
#endregion

#region ==================== PARTE 3: CIFRA DE SUBSTITUIÇÃO ====================
def decifar_subtituicao(texto_cifrado, chave):
    """
    Decifra texto usando Cifra de Substituição
    Substituir cada letra por outra baseada na chave
    """
    alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" #Inicia com alfabeto normal
    chave = chave.upper()
    
    # Cria mapa de tradução: chave -> alfabeto normal
    mapa_traducao = str.maketrans(chave, alfabeto)
    
    return texto_cifrado.upper().translate(mapa_traducao)

def hill_climbing_substitution(texto_cifrado, analisador, max_iteracoes=4000):
    """
    Quebra a cifra de substituição usando hill climbing
    """
    melhor_chave_global = None
    melhor_pontuacao_global = float('-inf')
    
    for _ in range(3):
        # Começa com chave aleatória
        chave_inicial = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        random.shuffle(chave_inicial)
        
        melhor_chave = "".join(chave_inicial)
        melhor_pontuacao = analisador.calcular_pontuacao(
            decifar_subtituicao(texto_cifrado, melhor_chave)
        )
        
        # Temperatura inicial para simulated annealing
        temperatura = 20
        resfriamento = 0.95
        
        # Algoritmo de hill climbing com simulated annealing
        sem_melhoria = 0
        for iteracao in range(max_iteracoes):
            # Cria nova chave trocando duas letras aleatórias
            nova_chave_lista = list(melhor_chave)
            i, j = random.sample(range(26), 2)
            nova_chave_lista[i], nova_chave_lista[j] = nova_chave_lista[j], nova_chave_lista[i]
            nova_chave = "".join(nova_chave_lista)
            
            # Testa a nova chave
            novo_texto = decifar_subtituicao(texto_cifrado, nova_chave)
            nova_pontuacao = analisador.calcular_pontuacao(novo_texto)
            
            # Aceita se melhor ou probabilisticamente se pior
            delta = nova_pontuacao - melhor_pontuacao
            if delta > 0 or (temperatura > 0.01 and random.random() < math.exp(delta/temperatura)):
                melhor_chave = nova_chave
                melhor_pontuacao = nova_pontuacao
                sem_melhoria = 0
            else:
                sem_melhoria += 1
            
            if iteracao % 100 == 0:
                temperatura *= resfriamento
            
            if sem_melhoria > 500:
                temperatura = max(temperatura * 2, 5)
                sem_melhoria = 0
        
        # Atualiza melhor resultado global
        if melhor_pontuacao > melhor_pontuacao_global:
            melhor_chave_global = melhor_chave
            melhor_pontuacao_global = melhor_pontuacao

    texto_decifrado = decifar_subtituicao(texto_cifrado, melhor_chave_global)
    return melhor_chave_global, texto_decifrado
#endregion

#region ==================== PARTE 4: ANALISADOR DE TEXTO ====================
class AnalisadorTexto:    
    def __init__(self, arquivo_quadgrams):
        self.quadgrams = {}
        total = 0
        
        # Carrega estatísticas de grupos de 4 letras
        with open(arquivo_quadgrams, 'r') as arquivo:
            for linha in arquivo:
                partes = linha.strip().split()
                if len(partes) == 2:
                    quadgram, contagem = partes
                    contagem = int(contagem)
                    self.quadgrams[quadgram] = contagem
                    total += contagem
        
        # Converte para probabilidades (logaritmo)
        for quadgram in self.quadgrams:
            probabilidade = float(self.quadgrams[quadgram]) / total
            self.quadgrams[quadgram] = math.log10(probabilidade)
        
        # Valor mínimo para grupos não encontrados
        self.valor_minimo = math.log10(0.01 / total)
    
    def calcular_pontuacao(self, texto):
        # Remove caracteres não-alfabéticos
        texto_limpo = re.sub(r'[^A-Z]', '', texto.upper())
        pontuacao = 0
        
        # Analisa cada grupo de 4 letras
        for i in range(len(texto_limpo) - 3):
            grupo = texto_limpo[i:i+4]
            pontuacao += self.quadgrams.get(grupo, self.valor_minimo)
        
        return pontuacao
#endregion

# ==================== PARTE 5: PROGRAMA PRINCIPAL ====================
def main():
    # 1. LER ARQUIVO CODIFICADO
    try:
        with open('encoded.txt', 'r') as arquivo:
            texto_codificado = arquivo.read()
    except FileNotFoundError:
        print("Erro: Arquivo 'encoded.txt' não encontrado!")
        return
    
    # 2. CONFIGURAR ANALISADOR
    try:
        analisador = AnalisadorTexto('quadgrams.txt')
    except FileNotFoundError:
        print("Erro: Arquivo 'quadgrams.txt' não encontrado!")
        return
    
    print("INICIANDO...\n")
    
    print("PASSO 1: CONVERSÃO BINÁRIO → TEXTO")
    texto_apos_binario = binario_para_texto(texto_codificado)
    print(f"Texto após conversão:\n{texto_apos_binario}\n")
    
    print("PASSO 2: QUEBRANDO CIFRA DE CÉSAR")
    deslocamento, texto_apos_cesar = quebrar_cesar(texto_apos_binario, analisador)
    print(f"Melhor deslocamento: {deslocamento}")
    print(f"Texto após César:\n{texto_apos_cesar}\n")
    
    print("PASSO 3: QUEBRANDO CIFRA DE SUBSTITUIÇÃO")
    melhor_chave, texto_final = hill_climbing_substitution(texto_apos_cesar, analisador)
    
    print(f"Melhor chave encontrada: {melhor_chave}")
    print(f"TEXTO FINAL DECIFRADO:\n{texto_final}")

if __name__ == "__main__":
    main()