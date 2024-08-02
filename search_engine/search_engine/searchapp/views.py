from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def index(request):
    return render(request, 'index.html')

def search_result(request):
    if request.method == 'GET' and 'q' in request.GET:
        query = request.GET['q']
    else:
        return HttpResponse('No query provided.')

    nltk.download('punkt')
    nltk.download('stopwords')

    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()

    file_path = 'C:/Users/Lenovo/OneDrive/Desktop/Assingment/Task 1/research.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 4), analyzer='char')

    processed_query = preprocess_text(query, ps, stop_words)
    processed_documents = preprocess_documents(data, ps, stop_words)

    tfidf_matrix = tfidf_vectorizer.fit_transform(processed_documents)
    query_vector = tfidf_vectorizer.transform([processed_query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    results = get_search_results(data, cosine_similarities)

   # Pagination
    paginator = Paginator(results, 10)  # Show 10 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'results': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'results.html', context)


def preprocess_text(text, stemmer, stop_words):
    tokens = nltk.word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
    return ' '.join(stemmed_tokens)

def preprocess_documents(data, stemmer, stop_words):
    processed_documents = []
    for item in data:
        title = preprocess_text(item['title'], stemmer, stop_words)
        authors = preprocess_authors(item['authors'], stemmer, stop_words)
        combined_document = f"{title} {' '.join(authors)}"
        processed_documents.append(combined_document)
    return processed_documents

def preprocess_authors(authors, stemmer, stop_words):
    authors_processed = []
    for author in authors:
        author_name = preprocess_text(author['name'], stemmer, stop_words)
        authors_processed.append(author_name)
    return authors_processed

def get_search_results(data, cosine_similarities):
    sorted_indices = cosine_similarities.argsort()[::-1]
    results = []
    for i in sorted_indices:
        relevance_score = cosine_similarities[i]
        item = data[i]
        title = item['title']
        authors = item['authors']
        processed_authors = [{'name': author['name'], 'link': author.get('profile_link', '#')} for author in authors]
        result = {
            'title': title,
            'publication_link': item['publication_link'],
            'authors': processed_authors,
            'publication_year': item['publication_year'],
            'relevance_score': relevance_score
        }
        results.append(result)
    return results
