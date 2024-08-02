from django.shortcuts import render
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# Function to download necessary NLTK resources
def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Function to preprocess documents
def preprocess_documents(documents):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    processed_docs = []
    for doc in documents:
        tokens = nltk.word_tokenize(doc)
        words = [lemmatizer.lemmatize(word.lower()) for word in tokens if word.isalnum() and word.lower() not in stop_words]
        processed_docs.append(' '.join(words))
    
    return processed_docs

# Function to perform clustering
def perform_clustering(documents, n_clusters):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_df=0.95, min_df=4)
    X = vectorizer.fit_transform(documents)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X)

    return kmeans, X, vectorizer

# Function to calculate silhouette score
def calculate_silhouette_score(X, kmeans):
    pca = PCA(n_components=2)
    X_reduced = pca.fit_transform(X.toarray())
    score = silhouette_score(X_reduced, kmeans.labels_)
    return score

# Function to get top words for each cluster
def get_top_words(kmeans, vectorizer, n_clusters):
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    top_words = {}
    for i in range(n_clusters):
        top_words[i] = [terms[ind] for ind in order_centroids[i, :10]]
        print(f"Cluster {i} top words: {top_words[i]}")
    return top_words

# View function to handle the cluster view
def cluster_view(request):
    return render(request, 'cluster.html')

# View function to handle the cluster result
def cluster_result(request):
    csv_path = 'C:/Users/Lenovo/OneDrive/Desktop/Assingment/Task 1/search_engine/newsdata.csv'
    df = pd.read_csv(csv_path, encoding='latin-1')

    download_nltk_resources()
    processed_docs = preprocess_documents(df['Document'])

    n_clusters = min(len(df['Document']), 3)
    kmeans, X, vectorizer = perform_clustering(processed_docs, n_clusters)

    silhouette_avg = calculate_silhouette_score(X, kmeans)
    print("Silhouette Score:", silhouette_avg)
    top_words = get_top_words(kmeans, vectorizer, n_clusters)

    if request.method == 'POST':
        new_doc = request.POST.get('document')
        new_processed_doc = preprocess_documents([new_doc])
        new_X = vectorizer.transform(new_processed_doc)

        predicted = kmeans.predict(new_X)[0]
        cluster_categories = {0: "Politics", 1: "Entertainment", 2: "Ecomomy"}
        cluster_category = cluster_categories.get(predicted, 'unknown')

        context = {
            'cluster_category': cluster_category,
            # 'silhouette_avg': silhouette_avg,
        }
        return render(request, 'result.html', context)

    return render(request, 'cluster.html')
