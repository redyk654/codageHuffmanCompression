import heapq
import os
import pickle
import argparse

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def generate_codes(node, prefix="", code_map=None):
    if code_map is None:
        code_map = {}
    if node:
        if node.char is not None:
            code_map[node.char] = prefix
        generate_codes(node.left, prefix + "0", code_map)
        generate_codes(node.right, prefix + "1", code_map)
    return code_map

def compress_file(input_file, output_file):
    # Étape 1 : Lire le fichier et calculer les fréquences
    with open(input_file, 'r') as file:
        data = file.read()
    frequencies = {char: data.count(char) for char in set(data)}
    
    # Étape 2 : Construire l'arbre de Huffman et générer les codes
    root = build_huffman_tree(frequencies)
    codes = generate_codes(root)

    # Étape 3 : Encoder les données
    encoded_data = ''.join(codes[char] for char in data)

    # Étape 4 : Convertir en octets et enregistrer
    padded_data = encoded_data + '0' * ((8 - len(encoded_data) % 8) % 8)
    byte_data = bytearray(int(padded_data[i:i+8], 2) for i in range(0, len(padded_data), 8))

    with open(output_file, 'wb') as file:
        pickle.dump((byte_data, codes), file)  # Stocker les données compressées et le dictionnaire

    print(f"Compression terminée : {input_file} → {output_file}")


def decompress_file(compressed_file, output_file):
    with open(compressed_file, 'rb') as file:
        byte_data, codes = pickle.load(file)

    # Reconstruire l'arbre de Huffman
    reverse_codes = {v: k for k, v in codes.items()}
    bit_string = ''.join(f"{byte:08b}" for byte in byte_data)

    # Supprimer le padding
    current_code = ""
    decoded_data = []
    for bit in bit_string:
        current_code += bit
        if current_code in reverse_codes:
            decoded_data.append(reverse_codes[current_code])
            current_code = ""

    # Écrire les données dans le fichier de sortie
    with open(output_file, 'w') as file:
        file.write(''.join(decoded_data))

    print(f"Décompression terminée : {compressed_file} → {output_file}")


def calculer_taux_compression(taille_originale, taille_compressee):
    """
    Calcule le taux de compression en pourcentage.
    
    :param taille_originale: Taille du fichier original en octets
    :param taille_compressee: Taille du fichier compressé en octets
    :return: Taux de compression en pourcentage
    """
    return (1 - taille_compressee / taille_originale) * 100

# Fonction principale
def main():
    # Configuration du parser pour les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Compression de fichiers avec le codage de Huffman")
    parser.add_argument(
        "fichier",
        type=str,
        help="Chemin du fichier à compresser"
    )
    args = parser.parse_args()

    input_file = args.fichier

    # Vérifier si le fichier existe
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier '{input_file}' n'existe pas.")
        return

    compressed_file = 'sample_compressed.huff'

    # compression
    compress_file(input_file, compressed_file)
    # décompression
    decompress_file(compressed_file, 'sample_decompressed.txt')

    # Vérifier la taille des fichiers
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(compressed_file)

    print(f"Taille du fichier original : {original_size} octets")
    print(f"Taille du fichier compressé : {compressed_size} octets")
    # taux de compression
    print(f"Taux de compression : {calculer_taux_compression(original_size, compressed_size):.2f}%")

if __name__ == "__main__":
    main()
