import pandas as pd
import networkx as nx
import tkinter as tk

data_path_uData = 'ml-100k/u.data'
data_path_uItem = 'ml-100k/u.item'


ratings_df = pd.read_csv(data_path_uData, sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'], encoding='latin-1')
movies_df = pd.read_csv(data_path_uItem, sep='|', names=['movie_id', 'title'], usecols=[0, 1], encoding='latin-1')

movie_id_to_title = dict(zip(movies_df['movie_id'], movies_df['title']))

movie_graph = {}
G = nx.DiGraph()

for movie_id, title in movie_id_to_title.items():
    G.add_node(movie_id, title=title)

for _, row in ratings_df.iterrows():
    user_id = row['user_id']
    movie_id = row['movie_id']
    rating = row['rating']

    G.add_edge(user_id, movie_id, weight=rating)

def recommend_movies(graph, user_id, num_recommendations=10):
    recommendations = []

    def dfs_modified(node, depth):
        nonlocal recommendations

        if depth == 0:
            return

        neighbors = list(graph.neighbors(node))

        neighbor_scores = {}
        for neighbor in neighbors:
            edge_data = graph.get_edge_data(node, neighbor)
            weight = edge_data['weight']
            neighbor_scores[neighbor] = weight

        sorted_neighbors = sorted(neighbor_scores.items(), key=lambda x: x[1], reverse=True)

        for neighbor, score in sorted_neighbors:
            if neighbor not in recommendations:
                recommendations.append(neighbor)
                dfs_modified(neighbor, depth - 1)

    dfs_modified(user_id, num_recommendations)

    recommended_movies = [movie_id_to_title[movie_id] for movie_id in recommendations]

    return recommended_movies

def get_user_preferences():
    user_preferences = {}

    print("Informe os filmes que você gostou (separe com vírgulas):")
    liked_movies = input("Digite os nomes dos filmes: ")
    liked_movies = liked_movies.split(',')

    for movie in liked_movies:
        movie = movie.strip()
        user_preferences[movie] = 1.0 

    return user_preferences

def generate_recommendations(graph, user_preferences, user_id, num_recommendations=10):
    recommendations = []

    def dfs_from_preferences(node, depth):
        nonlocal recommendations

        if depth == 0:
            return

        neighbors = list(graph.neighbors(node))

        neighbor_scores = {}
        for neighbor in neighbors:
            edge_data = graph.get_edge_data(node, neighbor)
            weight = edge_data['weight']
            neighbor_scores[neighbor] = user_preferences.get(movie_id_to_title[neighbor], 0.0) * weight

        sorted_neighbors = sorted(neighbor_scores.items(), key=lambda x: x[1], reverse=True)

        for neighbor, score in sorted_neighbors:
            if neighbor not in recommendations:
                recommendations.append(neighbor)
                dfs_from_preferences(neighbor, depth - 1)

    dfs_from_preferences(user_id, num_recommendations)

    recommended_movies = [movie_id_to_title[movie_id] for movie_id in recommendations]

    return recommended_movies

root = tk.Tk()
root.title("Sistema de Recomendação de Filmes")

label = tk.Label(root, text="Informe os filmes que você gostou (separe com vírgulas):")
label.pack()

user_preferences = get_user_preferences()  

recommendations_button = tk.Button(root, text="Gerar Recomendações", command=lambda: display_recommendations())
recommendations_button.pack()

recommendations_label = tk.Label(root, text="Recomendações:")
recommendations_label.pack()
recommendations_listbox = tk.Listbox(root, height=30, width=100)  
recommendations_listbox.pack()

num_max_recommendations = 20

def display_recommendations():
    user_id = 1  
    num_recommendations = num_max_recommendations  
    recommended_movies = generate_recommendations(G, user_preferences, user_id, num_recommendations)
    recommendations_listbox.delete(0, tk.END)
    for i, movie in enumerate(recommended_movies[:num_max_recommendations]):
        recommendations_listbox.insert(i, f"{i + 1}. {movie}")

root.mainloop()



