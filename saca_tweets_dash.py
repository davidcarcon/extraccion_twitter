import streamlit as st
import pandas as pd
import tweepy

@st.cache
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def cambio_username():
        st.session_state.username = False
def cambio_concepto():
        st.session_state.concepto = False

def oauth_login():
        ''' 
        Acceso a API twitter
        '''
        consumer_key = st.secrets['consumer_key']
        consumer_secret = st.secrets['consumer_secret']
        access_token = st.secrets['access_token']
        access_token_secret = st.secrets['access_token_secret']
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        return api

def extrae_guarda_tuits(acceso, listaConceptos, cuantos):
	'''
	Busca tuits con los username
	'''
	dftuits = pd.DataFrame()
	dfusers = pd.DataFrame()
	for concepto in listaConceptos:
		status_u = acceso.get_user(id=concepto)
		registro_usuario = {
			'Nombre': str(status_u._json["name"]),
			'Usuario_twitter': str(status_u._json["screen_name"]),
			'Ubicacion': str(status_u._json["location"]),
			'Descripcion': str(status_u._json["description"].replace('\n', '')),
			'Numero_followers': str(status_u._json["followers_count"])
		}
		dfusers = dfusers.append(registro_usuario, ignore_index=True)
		for status in tweepy.Cursor(acceso.user_timeline, 
									id=concepto,
									tweet_mode="extended").items(cuantos):
			registro = {
				'Fecha_creacion': status._json['created_at'],
				'Usuario_twitter': status._json['user']['screen_name'],
				'Texto': status._json["full_text"]
			}
			dftuits = dftuits.append(registro, ignore_index=True)
	return dfusers, dftuits

def extrae_tuits_concepto(acceso, listaConceptos, cuantos):
	'''
	Busca tuits por conceptos
	'''
	dfusuariospro = pd.DataFrame()
	dftotal = pd.DataFrame()
	for concepto in listaConceptos:
		for status in tweepy.Cursor(api.search_tweets, q=concepto, 
											 geocode='19.42847,-99.12766,2500km',
											 lang='es', result_type='recent',
											 include_entities=False,
											 tweet_mode='extended').items(cuantos):
			registro = {
				'Fecha_creacion': status._json['created_at'],
				'Usuario_twitter': status._json['user']['screen_name'],
				'Texto': status._json["full_text"]
			}
			dftotal = dftotal.append(registro, ignore_index=True)
	return dftotal

st.title('Extracción de Tweets :exclamation::exclamation:')

username = st.checkbox('UserNames', key='username', on_change=cambio_concepto)
concepto = st.checkbox('Conceptos', key='concepto', on_change=cambio_username)

if username:
	usernames = st.text_area('Usuarios de Twitter separados por ,')
	if usernames != '':
		usernames = list(map(lambda x: x.strip(), usernames.split(',')))
		api = oauth_login()
		usuarios, textos = extrae_guarda_tuits(api, usernames, 5)
		csv_usuarios = convert_df(usuarios) 
		csv_textos = convert_df(textos)
		st.header('Información de los Usuarios :adult:')
		st.dataframe(usuarios)
		st.download_button(
			"Press to Download",
			csv_usuarios,
			"usuarios.csv",
			"text/csv",
			key='download-csv'
		)
		st.header('Muestra de los ultmos tuits de los usuarios :astonished:')
		st.dataframe(textos.sample(10))
		st.download_button(
			"Press to Download",
			csv_textos,
			"textos.csv",
			"text/csv",
			key='download-csv'
		)
if concepto:
	conceptos = st.text_area('Conceptos para buscar separados por ,')
	if conceptos != '':
		conceptos =  list(map(lambda x: x.strip(), conceptos.split(',')))
		api = oauth_login()
		st.header('Muestra de los tweets mas recientes de cada concepto :eyes:')
		df_salida = extrae_tuits_concepto(api, conceptos, 5)
		csv_salida = convert_df(df_salida)
		st.dataframe(df_salida)
		st.download_button(
			"Press to Download",
			csv_salida,
			"conceptos.csv",
			"text/csv",
			key='download-csv'
		)
