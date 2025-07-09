import matplotlib.pyplot as plt
import pymongo
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResGraphs:
    def __init__(self, connection_string, unitednations, resolutions):
        self.connection_string = connection_string
        self.unitednations = unitednations
        self.resolutions = resolutions
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[unitednations]
        self.collection = self.db[resolutions]

    def top_subjects_bar_graph(self, save_filename=None):
        """ goal is to find the top 10 subjects in the json and graph """
        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                "$unwind": "$subjects"
            },
            {
                "$group": {
                    "_id": "$subjects",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 10
            }
        ]

        # Execute the pipeline
        result = list(self.collection.aggregate(pipeline))

        # get the data
        subjects = [entry["_id"] for entry in result]
        counts = [entry["count"] for entry in result]

        # Plot
        plt.bar(subjects, counts)
        plt.xlabel("Subjects")
        plt.ylabel("Count")
        plt.title("Top 10 Most Frequent Subjects")
        plt.xticks(rotation=25, ha="right", fontsize=7)
        plt.tight_layout()

        # Save the plot to a png
        if save_filename:
            plt.savefig(save_filename, format="png")
        else:
            plt.show()

    def plot_average_voting_percentage(self, save_filename=None):
        """ within json, I had fitted a voting_yes percentage under a subfield. This allso for this graph.
        The goal: to show the average voting for each year over time """
        # Connect to MongoDB - added when i ran pipeline and plot through chatgpt
        client = pymongo.MongoClient(self.connection_string)
        db = client[self.unitednations]
        collection = db[self.resolutions]

        # MongoDB aggregation pipeline to calculate the average voting percentage for each year
        pipeline = [
            {
                "$match": {
                    "voting.voting_yes_percentage": {"$exists": True},
                    "year": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": "$year",
                    "average_percentage": {"$avg": "$voting.voting_yes_percentage"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        # Execute
        results = list(collection.aggregate(pipeline))

        # get the years and average percentages for x and y axes
        years = [result["_id"] for result in results]
        average_percentages = [result["average_percentage"] for result in results]

        # Set Seaborn style
        sns.set(style="whitegrid")

        # Plot
        plt.figure(figsize=(10, 6))
        sns.lineplot(x=years, y=average_percentages, marker='o', color='b')
        plt.title('Average Voting Percentage Over the Years')
        plt.xlabel('Year')
        plt.ylabel('Average Voting Percentage')
        # Save the plot as png
        if save_filename:
            plt.savefig(save_filename, format='png')

        plt.show()

    def calculate_similarity_matrix(self, save_filename=None):
        """ A similarity matrix to compare each organization and the topics they cover.
        Higher similarity between each org means they cover the same/more similar topics"""
        # Connect to MongoDB
        client = pymongo.MongoClient(self.connection_string)
        db = client[self.unitednations]
        collection = db[self.resolutions]

        # Aggregate and filter out documents with empty or None descriptions and topics
        grouped_documents = collection.aggregate([
            {"$match": {"description": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": {"$ifNull": ["$organization_un_entity", "No Organization Associated"]}, "combined_text": {"$push": {"$concat": ["$topics", " ", "$description"]}}}}
        ])

        # Filter out empty or None combined_text arrays
        grouped_documents = [group for group in grouped_documents if group['combined_text'] and len(group['combined_text']) > 1]

        # Select the top 10 organizations based on some criteria
        top_10_organizations = sorted(grouped_documents, key=lambda x: len(x['combined_text']), reverse=True)[:10]

        # Check if there are valid organizations for vectorization
        if not top_10_organizations:
            print("No valid organizations for vectorization.")
            return

        # Replace None values with "No Organization Associated" and join non-None strings from combined_texts
        combined_texts = [' '.join(filter(None, org['combined_text'])) for org in top_10_organizations]

        # Vectorize descriptions using TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(combined_texts)

        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Set Seaborn style
        sns.set(style="whitegrid")

        # Plotting the data with Seaborn style
        plt.figure(figsize=(10, 6))
        sns.heatmap(similarity_matrix, annot=True, cmap="YlGnBu", xticklabels=[org['_id'] for org in top_10_organizations],
                    yticklabels=[org['_id'] for org in top_10_organizations])
        #changing ticklabel size (otherwise they get cut off by png
        plt.xticks(rotation=25, ha='right', fontsize=7)
        plt.yticks(rotation=25, ha='right', fontsize=7)

        plt.title('Cosine Similarity Matrix (Top 10 Organizations)')
        plt.xlabel('Organization')
        plt.ylabel('Organization')

        # Save the plot as a PNG file if save_filename is specified
        if save_filename:
            plt.savefig(save_filename, format='png')

        plt.show()