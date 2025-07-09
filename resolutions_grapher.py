"""
resolutions_grapher.py
graphs the desired plots.
"""
from un_res_viz import ResGraphs

# initialize a connection using the mongodb connection string and giving database and class name
res_graphs = ResGraphs("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.1.4",
                       "unitednations", "resolutions")
res_graphs.plot_average_voting_percentage(save_filename="average_voting_percentage_plot.png")
res_graphs.calculate_similarity_matrix(save_filename="similarity_matrix_plot.png")
res_graphs.top_subjects_bar_graph(save_filename="top_subjects_bar_graph.png")