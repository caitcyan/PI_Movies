import streamlit as st
import pandas as pd
import numpy as np
import base64
from deta import Deta
from deta import Drive

st.set_page_config(layout="wide") #para ocupar toda la pantalla

deta = Deta("e0t3zaGELWHa_JjY9Bw5uJusD698dB1Qxqujkpo3h3SQy")
drive = deta.Drive("data")
large_file1 = drive.get('data_aux.csv')
with open("data_aux.csv", "wb+") as f:
  for chunk in large_file1.iter_chunks(4096):
      f.write(chunk)
  large_file1.close()

deta = Deta("e0t3zaGELWHa_JjY9Bw5uJusD698dB1Qxqujkpo3h3SQy")
drive = deta.Drive("data")
large_file2 = drive.get('new_data.csv')
with open("new_data.csv", "wb+") as f:
  for chunk in large_file2.iter_chunks(4096):
      f.write(chunk)
  large_file2.close()

deta = Deta("e0t3zaGELWHa_JjY9Bw5uJusD698dB1Qxqujkpo3h3SQy")
drive = deta.Drive("data")
large_file3 = drive.get('data.csv')
with open("data.csv", "wb+") as f:
  for chunk in large_file3.iter_chunks(4096):
      f.write(chunk)
  large_file3.close()

def load_data():
    data = pd.read_csv('data.csv', compression='gzip')
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    #Filtramos solo las peliculas
    data = data[data['type']=='movie']
    #Convertimos las demás columnas
    data['userid'] = data['userid'].astype(int)
    data['id'] = data['id'].astype(str)
    data['rating_y'] = data['rating_y'].astype(float)
    data.drop('unnamed: 0', axis = 1 ,inplace= True)
    data.drop('type',axis= 1, inplace= True)
    return data

def get_Movies_Titles():
    listado = pd.read_csv('data_aux.csv', usecols=['title'])
    return listado['title']
def get_users():
    listado_users = pd.read_csv('new_data.csv',compression = 'gzip')
    return listado_users['userId']

if (large_file2.closed == True) and (large_file3.closed == True):
    dataset = load_data()
    st.title('Movie Recommendations System')
    st.write('')
    st.subheader('by :violet[Na]:green[ta]:blue[lia] Gomez')
    st.text('Shall I watch this movie? Select your userID and movie. The system will tell you if we recommend it to you or not. Do not just play!')
    col1, col2, col3 = st.columns([4,2,3])
    with col1:
        st.write('')
        st.text('     Secret Movies Dataset(Disney,Hulu,Netflix,Amazon)')
        st.write('')
        st.write('')
        #st.dataframe(load_data(1000))
        st.dataframe(dataset.head(100))

    with col2:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.subheader('Input user id:')
        st.subheader('')
        st.subheader('Select movie title:')
        st.subheader('')
        st.subheader('')
        st.subheader('')
        st.header(':green[Response:]')
    with col3:
        st.write('')
        st.write('')
        col1,col2 = st.columns([1,2])
        with col1:
            st.write('')
        with col2:
            st.write('')
        userSelected= st.text_input('', max_chars=7)
        enableButton = False
        if userSelected != '':
            try:
                userSelected = int(userSelected)
                users = get_users()
                if userSelected in users.values:
                    #Hacer machine learning
                    st.markdown("Great choice!")
                    enableButton = False
                else:
                    enableButton = True
                    st.markdown("This user is not valid. Try again")
            except:
                    #Error
                st.markdown("This user is not valid. Try again")
        
        arrayMovies = np.array(get_Movies_Titles())

        selectedMovie = st.selectbox('',arrayMovies)
        st.write('')
        st.write('')
        col1,col2 = st.columns([1,1])
        with col1:
            st.write('')
        with col2:
            clicked = st.button('Shall I watch this movie?', disabled = enableButton)

        def do_machine_learning(user,movie):
            from surprise import SVD
            from surprise import Reader
            from surprise.model_selection import train_test_split
            from surprise import Dataset
            dataset = pd.read_csv('new_data.csv', compression='gzip')
            data_aux = pd.read_csv('data_aux.csv')
            reader = Reader()
            N_filas = 100000 # Limitamos el dataset
            data = Dataset.load_from_df(dataset[['userId', 'newid', 'rating_y']][:N_filas], reader)
            trainset, testset = train_test_split(data, test_size=.3)
            model = SVD(n_factors=5) # Segun GridSearch
            # Entrenamos el modelo
            model.fit(trainset)
            predictions = model.test(testset)
            userId = int(user)
            rating = 4   # Tomamos películas a las que haya calificado con 4 o 5 estrellas
            if userId in dataset['userId']:
                df_user = dataset[(dataset['userId'] == userId) & (dataset['rating_y'] >= rating)]
                df_user = df_user.reset_index(drop=True)

            tabla_peliculas = data_aux[['title','newid']]
            vistas_usuario = dataset[dataset['userId'] == userId]
            peliculas_usuario = pd.merge(tabla_peliculas,vistas_usuario , how='outer', indicator=True)
            peliculas_del_usuario = peliculas_usuario.loc[peliculas_usuario._merge == 'left_only', ['newid','title']]
            peliculas_del_usuario['Estimate_Score'] = peliculas_del_usuario['newid'].apply(lambda x: model.predict(userId, x).est)
            peliculas_del_usuario = peliculas_del_usuario.sort_values('Estimate_Score', ascending=False)
            peliculas_del_usuario_filtradas = peliculas_del_usuario[peliculas_del_usuario['Estimate_Score']>4]
            

            if movie in peliculas_del_usuario_filtradas:
                recomended = True
                score = peliculas_del_usuario_filtradas[peliculas_del_usuario_filtradas['title'] == movie]
                score = score['Estimate_Score']
                score = np.array(score)
                score = float(score)
                return score, recomended
            else:
                recomended = False
                score = peliculas_del_usuario[peliculas_del_usuario['title'] == movie]
                score = score['Estimate_Score']
                score = np.array(score)
                score = float(score)
                return score, recomended

        if clicked:
            #Retorna true si está en la lista de recomendados para ese usuario
            score, recomendado = do_machine_learning(userSelected,selectedMovie)
            if recomendado:
                value = 'Yes'
            else:
                value = 'No'
            st.metric('Our estimated score for this movie is '+ str(round(score, 2)), value)

        st.write('')
        st.write('')



with open('background.gif', "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/{"gif"};base64,{encoded_string.decode()});
                background-attachment: fixed;
                background-size: cover
            }}
            </style>
            """,
            unsafe_allow_html=True
        )



css = '''
    <style>
    section.main > div:has(~ footer ) {
        padding-bottom: 5px;
    }
    </style>
    '''
st.markdown(css, unsafe_allow_html=True)

