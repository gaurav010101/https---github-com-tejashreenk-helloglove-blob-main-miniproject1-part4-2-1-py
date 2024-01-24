#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import numpy as np
import numpy.linalg as la
import pickle
import os
import gdown
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import math


# Compute Cosine Similarity
def cosine_similarity(x, y):
    """
    Exponentiated cosine similarity
    1. Compute cosine similarity
    2. Exponentiate cosine similarity
    3. Return exponentiated cosine similarity
    """
    # Compute cosine similarity
    dot_product = np.dot(x, y)
    magnitude_x = np.linalg.norm(x)
    magnitude_y = np.linalg.norm(y)
    cosine_similarity = dot_product / (magnitude_x * magnitude_y)

    # Exponentiate cosine similarity
    exp_cosine_similarity = np.exp(cosine_similarity)

    # Return exponentiated cosine similarity
    return exp_cosine_similarity

if 'text_search' in st.session_state:
    # Here, you need to define x and y based on your application logic.
    # For now, I'm using placeholder random vectors for demonstration.
    x = np.random.rand(10)  # Replace with your actual data
    y = np.random.rand(10)  # Replace with your actual data

    # Calculate cosine similarity for example vectors
    result = cosine_similarity(x, y)
    st.write("Cosine Similarity:", result)
    

# Function to Load Glove Embeddings
def load_glove_embeddings(glove_path="embeddings.pkl"):
    with open(glove_path, "rb") as f:
        embeddings_dict = pickle.load(f, encoding="latin1")

    return embeddings_dict


def get_model_id_gdrive(model_type):
    if model_type == "25d":
        word_index_id = "13qMXs3-oB9C6kfSRMwbAtzda9xuAUtt8"
        embeddings_id = "1-RXcfBvWyE-Av3ZHLcyJVsps0RYRRr_2"
    elif model_type == "50d":
        embeddings_id = "1DBaVpJsitQ1qxtUvV1Kz7ThDc3az16kZ"
        word_index_id = "1rB4ksHyHZ9skes-fJHMa2Z8J1Qa7awQ9"
    elif model_type == "100d":
        word_index_id = "1-oWV0LqG3fmrozRZ7WB1jzeTJHRUI3mq"
        embeddings_id = "1SRHfX130_6Znz7zbdfqboKosz-PfNvNp"
        
    return word_index_id, embeddings_id


def download_glove_embeddings_gdrive(model_type):
    # Get glove embeddings from google drive
    word_index_id, embeddings_id = get_model_id_gdrive(model_type)

    # Use gdown to get files from google drive
    embeddings_temp = "embeddings_" + str(model_type) + "_temp.npy"
    word_index_temp = "word_index_dict_" + str(model_type) + "_temp.pkl"

    # Download word_index pickle file
    print("Downloading word index dictionary....\n")
    gdown.download(id=1m-X9Y7APEbmlTX5NFZ1viiC837N4hQjZ, output=word_index_temp, quiet=False)

    # Download embeddings numpy file
    print("Donwloading embedings...\n\n")
    gdown.download(id=1F0i_wCuTI2M632VCV-Oa2xM7rZiTC08X, output=embeddings_temp, quiet=False)


# @st.cache_data()
def load_glove_embeddings_gdrive(model_type):
    word_index_temp = "word_index_dict_" + str(model_type) + "_temp.pkl"
    embeddings_temp = "embeddings_" + str(model_type) + "_temp.npy"

    # Load word index dictionary
    word_index_dict = pickle.load(open(word_index_temp, "rb"), encoding="latin")

    # Load embeddings numpy
    embeddings = np.load(embeddings_temp)

    return word_index_dict, embeddings


@st.cache_resource()
def load_sentence_transformer_model(model_name):
    sentenceTransformer = SentenceTransformer(model_name)
    return sentenceTransformer


def get_sentence_transformer_embeddings(sentence, model_name="all-MiniLM-L6-v2"):
    """
    Get sentence transformer embeddings for a sentence
    """
    # 384 dimensional embedding
    # Default model: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2  

    sentenceTransformer = load_sentence_transformer_model(model_name)

    try:
        return sentenceTransformer.encode(sentence)
    except:
        if model_name == "all-MiniLM-L6-v2":
            return np.zeros(384)
        else:
            return np.zeros(512)


def get_glove_embeddings(word, word_index_dict, embeddings, model_type):
    """
    Get glove embedding for a single word
    """
    if word.lower() in word_index_dict:
        return embeddings[word_index_dict[word.lower()]]
    else:
        return np.zeros(int(model_type.split("d")[0]))


def averaged_glove_embeddings_gdrive(sentence, word_index_dict, embeddings, model_type=50):
    """
    Get averaged glove embeddings for a sentence
    1. Split sentence into words
    2. Get embeddings for each word
    3. Add embeddings for each word
    4. Divide by number of words
    5. Return averaged embeddings
    """
    # Initialize an embedding vector with zeros
    embedding_dim = int(model_type.split("d")[0])
    embedding = np.zeros(embedding_dim)

    # Split sentence into words
    words = sentence.split()

    # Keep track of the number of words found in the embedding dictionary
    valid_words_count = 0

    # Iterate over each word in the sentence
    for word in words:
        # Check if the word is in the word index dictionary
        if word in word_index_dict:
            # Add the embedding for this word
            embedding += embeddings[word_index_dict[word]]
            valid_words_count += 1

    # Check if there were valid words to avoid division by zero
    if valid_words_count > 0:
        # Divide by the number of valid words to get the average
        embedding /= valid_words_count

    # Return the averaged embeddings
    return embedding

def get_category_embeddings(embeddings_metadata):
    """
    Get embeddings for each category
    1. Split categories into words
    2. Get embeddings for each word
    """
    model_name = embeddings_metadata["model_name"]
    st.session_state["cat_embed_" + model_name] = {}
    for category in st.session_state.categories.split(" "):
        if model_name:
            if not category in st.session_state["cat_embed_" + model_name]:
                st.session_state["cat_embed_" + model_name][category] = get_sentence_transformer_embeddings(category, model_name=model_name)
        else:
            if not category in st.session_state["cat_embed_" + model_name]:
                st.session_state["cat_embed_" + model_name][category] = get_sentence_transformer_embeddings(category)


def update_category_embeddings(embedings_metadata):
    """
    Update embeddings for each category
    """
    get_category_embeddings(embeddings_metadata)


def get_sorted_cosine_similarity(embeddings_metadata):
    """
    Get sorted cosine similarity between input sentence and categories
    Steps:
    1. Get embeddings for input sentence
    2. Get embeddings for categories (if not found, update category embeddings)
    3. Compute cosine similarity between input sentence and categories
    4. Sort cosine similarity
    5. Return sorted cosine similarity
    (50 pts)
    """
    # Ask TA
    categories = st.session_state.categories.split(" ")
    cosine_sim = {}
    category_embeddings
    input_embedding
    if embeddings_metadata["embedding_model"] == "glove":
        word_index_dict = embeddings_metadata["word_index_dict"]
        embeddings = embeddings_metadata["embeddings"]
        model_type = embeddings_metadata["model_type"]

        input_embedding = averaged_glove_embeddings_gdrive(st.session_state.text_search,
                                                            word_index_dict,
                                                            embeddings, model_type)
        
        ##########################################
        ## TODO: Get embeddings for categories ###
        ##########################################
        st.session_state["cat_embed_" + model_name] = {}
        if categories != None:
            # Get and compute embeddings for each category
            for category in categories:
                category_embeddings.append(averaged_glove_embeddings_gdrive(category,word_index_dict,embeddings, model_type))


    else:
        model_name = embeddings_metadata["model_name"]
        if not "cat_embed_" + model_name in st.session_state:
            get_category_embeddings(embeddings_metadata)

        category_embeddings = st.session_state["cat_embed_" + model_name]

        print("text_search = ", st.session_state.text_search)
        if model_name:
            input_embedding = get_sentence_transformer_embeddings(st.session_state.text_search, model_name=model_name)
        else:
            input_embedding = get_sentence_transformer_embeddings(st.session_state.text_search)
    
    for index in range(len(categories)):
        ##########################################
        # TODO: Compute cosine similarity between input sentence and categories
        # TODO: Update category embeddings if category not found
        ##########################################
        category_embedding = category_embeddings[index]
        cosine_sim[categories[index]] = cosine_similarity(input_embedding, category_embedding)
    
    # Sort cosine similarities in descending order
    sorted_cosine_sim = sorted(cosine_sim.items(), key=lambda x: x[1], reverse=True)


    return sorted_cosine_sim


def plot_piechart(sorted_cosine_scores_items):
    sorted_cosine_scores = np.array([
            sorted_cosine_scores_items[index][1]
            for index in range(len(sorted_cosine_scores_items))
        ]
    )
    categories = st.session_state.categories.split(" ")
    categories_sorted = [
        categories[sorted_cosine_scores_items[index][0]]
        for index in range(len(sorted_cosine_scores_items))
    ]
    fig, ax = plt.subplots()
    ax.pie(sorted_cosine_scores, labels=categories_sorted, autopct="%1.1f%%")
    st.pyplot(fig)  # Figure


def plot_piechart_helper(sorted_cosine_scores_items):
    sorted_cosine_scores = np.array(
        [
            sorted_cosine_scores_items[index][1]
            for index in range(len(sorted_cosine_scores_items))
        ]
    )
    categories = st.session_state.categories.split(" ")
    categories_sorted = [
        categories[sorted_cosine_scores_items[index][0]]
        for index in range(len(sorted_cosine_scores_items))
    ]
    fig, ax = plt.subplots(figsize=(3, 3))
    my_explode = np.zeros(len(categories_sorted))
    my_explode[0] = 0.2
    if len(categories_sorted) == 3:
        my_explode[1] = 0.1  # explode this by 0.2
    elif len(categories_sorted) > 3:
        my_explode[2] = 0.05
    ax.pie(
        sorted_cosine_scores,
        labels=categories_sorted,
        autopct="%1.1f%%",
        explode=my_explode,
    )

    return fig


def plot_piecharts(sorted_cosine_scores_models):
    scores_list = []
    categories = st.session_state.categories.split(" ")
    index = 0
    for model in sorted_cosine_scores_models:
        scores_list.append(sorted_cosine_scores_models[model])
        # scores_list[index] = np.array([scores_list[index][ind2][1] for ind2 in range(len(scores_list[index]))])
        index += 1

    if len(sorted_cosine_scores_models) == 2:
        fig, (ax1, ax2) = plt.subplots(2)

        categories_sorted = [
            categories[scores_list[0][index][0]] for index in range(len(scores_list[0]))
        ]
        sorted_scores = np.array(
            [scores_list[0][index][1] for index in range(len(scores_list[0]))]
        )
        ax1.pie(sorted_scores, labels=categories_sorted, autopct="%1.1f%%")

        categories_sorted = [
            categories[scores_list[1][index][0]] for index in range(len(scores_list[1]))
        ]
        sorted_scores = np.array(
            [scores_list[1][index][1] for index in range(len(scores_list[1]))]
        )
        ax2.pie(sorted_scores, labels=categories_sorted, autopct="%1.1f%%")

    st.pyplot(fig)

def plot_alatirchart(sorted_cosine_scores_models):
    models = list(sorted_cosine_scores_models.keys())
    tabs = st.tabs(models)
    figs = {model: plot_piechart_helper(sorted_cosine_scores_models[model]) for model in models}

    for index, model in enumerate(models):
        with tabs[index]:
            st.pyplot(figs[model])

# Streamlit UI setup
st.sidebar.title("GloVe Twitter")
st.sidebar.markdown(
    """
    GloVe is an unsupervised learning algorithm for obtaining vector representations for words. Pretrained on 
    2 billion tweets with a vocabulary size of 1.2 million. Download from [Stanford NLP](http://nlp.stanford.edu/data/glove.twitter.27B.zip). 

    Jeffrey Pennington, Richard Socher, and Christopher D. Manning. 2014. *GloVe: Global Vectors for Word Representation*.
    """
)

model_type = st.sidebar.selectbox("Choose the model", ("25d", "50d"), index=1)

st.title("Search Based Retrieval Demo")
st.subheader("Pass in space separated categories you want this search demo to be about.")
categories = st.text_input(label="Categories", value="Flowers Colors Cars Weather Food")
print(categories)
print(type(categories))

st.subheader("Pass in an input word or even a sentence")
text_search = st.text_input(
    label="Input your sentence",
    value="Roses are red, trucks are blue, and Seattle is grey right now",
)

# Check if embeddings exist
embeddings_path = f"embeddings_{model_type}_temp.npy"
word_index_dict_path = f"word_index_dict_{model_type}_temp.pkl"

if not os.path.isfile(embeddings_path) or not os.path.isfile(word_index_dict_path):
    print(f"Model type = {model_type}")
    glove_path = f"glove_{model_type}.pkl"
    print(f"glove_path = {glove_path}")

    # Download embeddings
    with st.spinner("Downloading glove embeddings..."):
        download_glove_embeddings_gdrive(model_type)

# Load glove embeddings
word_index_dict, embeddings = load_glove_embeddings_gdrive(model_type)

if text_search:
    # Glove embeddings
    print("Glove Embedding")
    glove_embeddings_metadata = {
        "embedding_model": "glove",
        "word_index_dict": word_index_dict,
        "embeddings": embeddings,
        "model_type": model_type,
    }
    with st.spinner("Obtaining Cosine similarity for GloVe..."):
        sorted_cosine_sim_glove = get_sorted_cosine_similarity(text_search, glove_embeddings_metadata)

    # Sentence transformer embeddings
    print("Sentence Transformer Embedding")
    transformer_embeddings_metadata = {"embedding_model": "transformers", "model_name": ""}
    with st.spinner("Obtaining Cosine similarity for 384d sentence transformer..."):
        sorted_cosine_sim_transformer = get_sorted_cosine_similarity(text_search, transformer_embeddings_metadata)

    # Display results
    print(f"Categories are: {categories}")
    st.subheader(f"Closest word I have between: {categories} as per different Embeddings")

    # Plot Pie Chart
    plot_alatirchart({
        f"glove_{model_type}": sorted_cosine_sim_glove,
        "sentence_transformer_384": sorted_cosine_sim_transformer,
    })

    st.write("Demo developed by [Dr. Karthik Mohan Mohan](https://www.linkedin.com/in/karthik-mohan
