import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math
from tkinter import * 


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # raio médio da Terra em quilômetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def dijkstra_shortest_path(G, source, target):
    # inicialização dos dicionários de distância e predecessores
    dist = {node: float('inf') for node in G.nodes()}
    pred = {node: None for node in G.nodes()}
    
    # distância do nó de origem para si mesmo é zero
    dist[source] = 0
    
    # criação do conjunto de nós não visitados
    unvisited = set(G.nodes())
    
    while unvisited:
        # encontra o nó não visitado com a menor distância
        current_node = min(unvisited, key=lambda node: dist[node])
        
        # remove o nó atual do conjunto de não visitados
        unvisited.remove(current_node)
        
        # se o nó atual for o nó de destino, o algoritmo pode parar
        if current_node == target:
            break
        
        # atualização das distâncias dos vizinhos do nó atual
        for neighbor, edge_attr in G[current_node].items():
            alt = dist[current_node] + edge_attr['weight']
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                pred[neighbor] = current_node
    
    # se o nó de destino não foi alcançado, não há caminho
    if pred[target] is None:
        return None
    
    # reconstrução do caminho a partir dos predecessores
    path = [target]
    node = target
    while node != source:
        node = pred[node]
        path.append(node)
    path.reverse()
    
    # cálculo do custo do caminho
    cost = []
    for i in range(len(path) - 1):
        cost.append(G[path[i]][path[i+1]]['weight'])
    
    return path, cost

def imprime_dijkstra():
    global G, origem, destino, label_resultado
    if origem.get() == "" or destino.get() == "":
        label_resultado['text'] = "Não há informações suficientes."
    elif (origem.get().isnumeric() == False) or (destino.get().isnumeric() == False):
        label_resultado['text'] = "Um dos nós não pertence ao grafo."
    elif (int(origem.get()) not in G.nodes()) or (int(destino.get()) not in G.nodes()):
        label_resultado['text'] = "Um dos nós não pertence ao grafo."
    else:
        caminho = dijkstra_shortest_path(G, int(origem.get()), int(destino.get()))
        if caminho == None:
            label_resultado['text'] = f"Não há caminho de {origem.get()} até {destino.get()}."
        else:
            contador = 0
            string = f"O caminho de {origem.get()} até {destino.get()} será:\n"

            for i in caminho[0]:
                if len(caminho[0]) == contador + 1:
                    break
                string += str(i)
                string += '->'
                numero = caminho[0][contador + 1]
                string += str(numero)
                string +=  f"{': ' + str(caminho[1][contador])}"
                string += f" ({G.nodes[i]['name']} -> {G.nodes[numero]['name']})"
                string += '\n'
                contador += 1 
            distancia_total = (str(sum(caminho[1]))).split('.')
            string += f"A distância total será de {distancia_total[0]} km e {distancia_total[1][:3]} metros."
            label_resultado['text'] = string

            # plotagem do menor caminho no grafo
            menor_caminho = G.subgraph(caminho[0])
            pos = nx.get_node_attributes(G, 'pos')
            edge_labels = nx.get_edge_attributes(menor_caminho, 'weight')
            nx.draw_networkx(menor_caminho, pos=pos, with_labels=True, labels={node: G.nodes[node]['name'] for node in menor_caminho.nodes()}, font_size=8, node_size=50, width=1)
            nx.draw_networkx_edge_labels(menor_caminho, pos=pos, edge_labels=edge_labels, font_size=6)
            plt.show()


def plot_grafo_completo():
    global G
    pos = nx.get_node_attributes(G, 'pos')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx(G, pos=pos, with_labels=True, labels={node: G.nodes[node]['name'] for node in G.nodes()}, font_size=8, node_size=50, width=0.5)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_size=6)
    return plt.show()

def plot_grafo(grafo):
    pos = nx.get_node_attributes(grafo, 'pos')
    nx.draw_networkx_nodes(grafo, pos=pos, node_size=50)
    nx.draw_networkx_edges(grafo, pos=pos, width=0.5)
    return plt.show()

def print_grafo(grafo):
    edgelist = nx.generate_edgelist(grafo)
    for line in edgelist:
        print(line)


# Leitura do arquivo CSV
df = pd.read_csv('https://data.cityofnewyork.us/views/kk4q-3rt2/rows.csv')

# Substituição da barra (/) pelo hífen (-) na coluna NAME
df['NAME'] = df['NAME'].str.replace('/', '-')

# Criação do grafo
G = nx.Graph()

# Adição dos nós ao grafo
for idx, row in df.iterrows():
    pos = (row['the_geom'].split('POINT ')[1].replace('(', '').replace(')', '').split(' '))
    pos = (float(pos[0]), float(pos[1]))
    G.add_node(row['OBJECTID'], name=row['NAME'], pos=pos)

# Adição das arestas ao grafo
for idx1, row1 in df.iterrows():
    connected_lines = row1['LINE'].split('-')
    neighbors = []
    for idx2, row2 in df.iterrows():
        if idx1 != idx2:
            neighbor_lines = row2['LINE'].split('-')
            for line in connected_lines:
                if line in neighbor_lines:
                    pos1 = G.nodes[row1['OBJECTID']]['pos']
                    pos2 = G.nodes[row2['OBJECTID']]['pos']
                    neighbors.append((row2['OBJECTID'], round(haversine(pos1[1], pos1[0], pos2[1], pos2[0]), 3)))
                    break
    neighbors.sort(key=lambda x: x[1])
    added_edges = 0
    for neighbor in neighbors:
        if added_edges == len(connected_lines):
            break
        try:
            existing_edges = G[row1['OBJECTID']][neighbor[0]]
            shared_lines = [line for line in connected_lines if line in existing_edges['lines']]
            if len(shared_lines) == 0:
                G.add_edge(row1['OBJECTID'], neighbor[0], weight=neighbor[1], lines=connected_lines)
                added_edges += 1
        except KeyError:
            G.add_edge(row1['OBJECTID'], neighbor[0], weight=neighbor[1], lines=connected_lines)
            added_edges += 1

#ADICIONANDO ARESTAS QUE FALTAM
G.add_edge(99, 242, weight=round(haversine(40.60840218069683, -73.81583268782963, 40.66047600004959, -73.83030100071032), 3), lines=['A'])
G.add_edge(181, 182, weight=round(haversine(40.59294299908617, -73.77601299999507, 40.59237400121235, -73.7885219980118), 3), lines=['A'])
G.add_edge(332, 341, weight=round(haversine(40.60773573171741, -74.00159259239406, 40.61145578989005, -73.98178001069293), 3), lines=['N'])
G.add_edge(137, 148, weight=round(haversine(40.724479997808274, -73.95118300016523, 40.71277400073426, -73.9514239994525), 3), lines=['G'])
G.add_edge(266, 268, weight=round(haversine(40.87456099941789, -73.90983099923551, 40.86944399946045, -73.91527899954356), 4), lines=['1'])
G.add_edge(157, 156, weight=round(haversine(40.8340410001399, -73.94488999901047, 40.82655099962194, -73.95035999879713), 3), lines=['1'])
G.add_edge(259, 260, weight=round(haversine(40.867760000885795, -73.89717400101743, 40.87341199980121, -73.89006400069478), 3), lines=['4'])
G.add_edge(175, 174, weight=round(haversine(40.85345300155693, -73.9076840015997, 40.8484800012369, -73.91179399884471), 3), lines=['4'])
G.add_edge(48, 47, weight=round(haversine(40.82823032742169, -73.92569199505733, 40.81830344372315, -73.9273847542618), 3), lines=['4'])
G.add_edge(146, 151, weight=round(haversine(40.73097497580066, -73.98168087489128, 40.71717399858899, -73.95666499806525), 3), lines=['L'])
G.add_edge(74, 211, weight=round(haversine(40.68886654246024, -73.90395860491864, 40.69551800114878, -73.90393400118631), 4), lines=['L'])



#CONFIGURAÇÕES DE JANELA
janela = Tk()
janela.title("Estações de Metrô de NY")
janela.geometry('700x600')
janela.resizable(width=FALSE, height=FALSE)
janela.configure(bg="#3dbf69")

#ENTRADA DE ORIGEM E DESTINO E SAÍDA DO ALGORITMO DE DIJKSTRA

label_origem = Label(text="Digite aqui a sua origem")
label_origem.grid(column=0, row=0, pady=10)

origem = Entry(janela)
origem.grid(column=0, row=1, pady=10)

label_origem = Label(text="Digite aqui o seu destino")
label_origem.grid(column=0, row=2, pady=10)

destino = Entry(janela)
destino.grid(column=0, row=3, pady=10)

resultado_dijkstra = Button(text="Executar algoritmo", command=imprime_dijkstra)
resultado_dijkstra.grid(column=0, row=4, pady=10)

label_resultado = Label(janela, text="Não há informações suficientes.")
label_resultado.place(x=200, y=15)

#BOTÃO DE VER GRAFO
botao = Button(janela, width=20, text="Ver Grafo", relief='raised', command=plot_grafo_completo)
botao.grid(column=0, row=5, pady=10, padx=10)

#MANTER JANELA ATIVA
janela.mainloop()