import streamlit as st
import pandas as pd

# Chargement des données à partir du fichier CSV
corrMatrix = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/8739c4022e74f605fa297f85707e233e3fb6c7a3/corrMatrix.csv',sep=',')
animeList = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/f19528c3544d6e6244b3b97d44b7505c5861305b/animeList.csv',sep=',')
popularMovies = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/popularMovies.csv',sep=',')
movieStats = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/movieStats.csv',sep=',')
mappedColumnsMoviestat = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/mappedColumnsMoviestat.csv',sep=',')
#mappedColumnsMoviestat = pd.DataFrame(mappedColumnsMoviestat)
mappedColumnsMoviestat = mappedColumnsMoviestat.set_index('name')
movieRatings1 = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/movieRatings1.csv',sep=',')
movieRatings2 = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/movieRatings2.csv',sep=',')
movieRatings3 = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/movieRatings3.csv',sep=',')
movieRatings4 = pd.read_csv('https://raw.githubusercontent.com/wTrystan/anime-recommandation/refs/heads/main/movieRatings4.csv',sep=',')
concat = [movieRatings1,movieRatings2,movieRatings3,movieRatings4]
movieRatings = pd.concat(concat)
unique_anime_ids = animeList['name']

# Initialisation des variables de session
if 'show_similarity_anime' not in st.session_state:
    st.session_state['show_similarity_anime'] = False

if 'show_similarity_list' not in st.session_state:
    st.session_state['show_similarity_list'] = False
    
if 'show_similarity_user' not in st.session_state:
    st.session_state['show_similarity_user'] = False


col1, col2, col3 = st.columns(3)

if col1.button('Similarity with an anime'):
    st.session_state['show_similarity_anime'] = True
    st.session_state['show_similarity_list'] = False
    st.session_state['show_similarity_user'] = False

if col2.button('Similarity with a list of anime'):
    st.session_state['show_similarity_anime'] = False
    st.session_state['show_similarity_list'] = True
    st.session_state['show_similarity_user'] = False

if col3.button('Similarity with your taste in anime'):
    st.session_state['show_similarity_anime'] = False
    st.session_state['show_similarity_list'] = False
    st.session_state['show_similarity_user'] = True
 
def SimilarityWith(name_anime):
    #SimilarityWith :
        animeRatings = movieRatings[name_anime]
        similarMovies = movieRatings.corrwith(animeRatings)
        similarMovies = similarMovies.dropna()
        similarMovies = pd.DataFrame(similarMovies)
        similarMovies.columns=['similarity']
        
        df = mappedColumnsMoviestat.join(similarMovies)
        df = df.sort_values(by='similarity', ascending=False)

        # Filtrer le DataFrame par les anime_id sélectionnés
        filtered_df1 = df['similarity'][1:len(df)]
        
            # Affichage des tableaux
        return filtered_df1

def SimilarityFromList(list):
    df=pd.DataFrame()
    taille = len(list)
    for name in list:
        df = pd.concat([df,SimilarityWith(name)], ignore_index=False, axis=0)
    
    newTable = df.reset_index()
    newTable = newTable.groupby('index')['similarity'].sum().sort_values(ascending=False)
    newTable = newTable.iloc[taille:taille+5]
    st.dataframe(newTable)

def SimilarityUser(listeUser):
    myRatings = pd.DataFrame.from_dict(listeUser, orient="index").sort_values(by=0, ascending=False)
    simCandidates = pd.Series()
    for i in range(0, len(myRatings.index)-1):
        # Retrieve similar movies to this one that I rated
        sims = corrMatrix[myRatings.index[i]].dropna()
        # Now scale its similarity by how well I rated this movie
        sims = sims.map(lambda x: x * myRatings.iloc[i,0])
        # Add the score to the list of similarity candidates
        simCandidates = pd.concat([simCandidates, sims])
    
    simCandidates.sort_values(inplace = True, ascending = False)
    simCandidates = simCandidates.groupby(simCandidates.index).sum()
    simCandidates.sort_values(inplace = True, ascending = False)
    filteredSims = simCandidates.drop(myRatings.index)
    st.dataframe(filteredSims)

# Affichage du menu pour le choix de l'anime
if st.session_state['show_similarity_anime']:
    selection1 = st.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None)
    # Création du bouton d'action
    if st.button('Find the best animes for me :'):
        st.dataframe(SimilarityWith(selection1)[1:10])


# Affichage du menu pour le choix de la liste d'anime
if st.session_state['show_similarity_list']:
    selection_list1 = st.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None, key='anime1')
    selection_list2 = st.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None, key='anime2')
    selection_list3 = st.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None, key='anime3')
    # Création du bouton d'action
    if st.button('Find the best animes for me :'):
        liste = [selection_list1,selection_list2,selection_list3]
        SimilarityFromList(liste)


# # Affichage du menu pour le choix selon les users
if st.session_state['show_similarity_user']:
    # Création de deux colonnes
    col_anime, col_ratings = st.columns(2)

    selection_list1 = col_anime.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None, key='anime1')
    ratings_1 = col_ratings.number_input('Entrez un nombre:',min_value=-1, max_value=10, key='ratings_1',step=1,value=None)
    selection_list2 = col_anime.selectbox('Choose an anime:', unique_anime_ids,placeholder="Choose an option",index=None, key='anime2')
    ratings_2 = col_ratings.number_input('Entrez un nombre:',min_value=-1, max_value=10, key='ratings_2',step=1,value=None)

    # Création du bouton d'action
    if st.button('Find the best animes for me :'):
        listeUser = {selection_list1: ratings_1, selection_list2: ratings_2}
        SimilarityFromList(listeUser)
