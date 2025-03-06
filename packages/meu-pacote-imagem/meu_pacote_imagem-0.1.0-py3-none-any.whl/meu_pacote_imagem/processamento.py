
from PIL import Image

def redimensionar_imagem(caminho_entrada, caminho_saida, tamanho=(800, 600)):
    imagem = Image.open(caminho_entrada)
    imagem = imagem.resize(tamanho)
    imagem.save(caminho_saida)
    print(f"Imagem salva em {caminho_saida}")
