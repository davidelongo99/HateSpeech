from hs_functions import search_twitter_info
import pandas as pd

"""
Data about deputies and senators of the XIX legislature were downloaed by querying 
the official 'Camera dei Deputati' and 'Senato della Repubblica' SPARQL databases :
- https://dati.camera.it/sparql
- https://dati.senato.it/sparql 
Then, deputies and senators Twitter official and verified account information were 
collected by calling the Twitter API.
"""

### DEPUTIES
deputati = pd.read_csv('./Data/deputati.csv')
deputati = deputati.drop(columns=['persona', 'info', 'aggiornamento',
                         'lista', 'dataNascita', 'luogoNascita', 'collegio', 'numeroMandati'])
deputati['name_surname'] = deputati['nome'].str.title() + ' ' + \
    deputati['cognome'].str.title()
deputati['chamber'] = 'Camera dei Deputati'
# rename columns
deputati = deputati.rename(columns={
                           'cognome': 'surname', 
                           'nome': 'name', 
                           'genere': 'gender', 
                           'nomeGruppo': 'parliamentary_group'})

# replace parties' names
deputati = deputati.replace({
    'parliamentary_group': {
        "FRATELLI D'ITALIA (18.10.2022)": "Fratelli d'Italia",
        "LEGA - SALVINI PREMIER (18.10.2022)": "Lega",
        "FORZA ITALIA - BERLUSCONI PRESIDENTE - PPE (18.10.2022)": "Forza Italia",
        "PARTITO DEMOCRATICO - ITALIA DEMOCRATICA E PROGRESSISTA (18.10.2022)": "Partito Democratico",
        "AZIONE - ITALIA VIVA - RENEW EUROPE (18.10.2022)": "Azione - Italia Viva",
        "NOI MODERATI (27.10.2022)": "Noi Moderati",
        "MOVIMENTO 5 STELLE (18.10.2022)": "Movimento 5 Stelle",
        "ALLEANZA VERDI E SINISTRA (27.10.2022)": "Alleanza Verdi e Sinistra",
        "MISTO (18.10.2022)": "Misto"
    },
    'gender': {
        'male': 'M',
        'female': 'F'
    }
})

# get twitter information about deputies
twitter_info_dep = search_twitter_info(deputati.name_surname, 'config.ini')
# rename column (to avoid confunding with the name in official database)
twitter_info_dep = twitter_info_dep.rename(columns={'name': 'twitter_name'})
# inner join of twitter information dataframe and official deputies dataframe
twitter_dep = pd.concat([deputati, twitter_info_dep],
                        axis=1, join="inner").drop(columns=['deputy'])
# select columns
twitter_dep = twitter_dep[['surname', 'name', 'name_surname', 'twitter_name',
                           'screen_name', 'followers_count', 'friends_count',
                           'statuses_count', 'gender', 'user_id', 'verified',
                           'parliamentary_group', 'chamber']]
# save as csv file
twitter_dep.to_csv('twitter_dep.csv')


### SENATORS

# read csv file and drop not relevant columns
senatori = pd.read_csv(
    './Data/senatori.csv').drop(columns=['gruppo', 'senatore', 'inizioAdesione', 'carica'])
# create new columns with name + surname, and chamber name
senatori['name_surname'] = senatori.nome + ' ' + senatori.cognome
senatori['chamber'] = 'Senato della Repubblica'
# rename columns
senatori = senatori.rename(
    columns={'cognome': 'surname', 'nome': 'name', 'nomeGruppo': 'parliamentary_group'})

# replace parties' names
senatori = senatori.replace({
    'parliamentary_group': {
        'MoVimento 5 Stelle': 'Movimento 5 Stelle',
        "Lega Salvini Premier - Partito Sardo d'Azione": "Lega",
        "Forza Italia - Berlusconi Presidente - PPE": "Forza Italia",
        "Partito Democratico - Italia Democratica e Progressista": "Partito Democratico",
        'Per le Autonomie (SVP-Patt, Campobase, Sud Chiama Nord)': 'Autonomie',
        "Azione-ItaliaViva-RenewEurope": "Azione - Italia Viva",
        "Civici d'Italia - Noi Moderati (UDC - Coraggio Italia - Noi con l'Italia - Italia al Centro) - MAIE": "Civici d'Italia - Noi Moderati - MAIE"
    }
})

# get twitter account information about senators
twitter_info_sen = search_twitter_info(senatori.name_surname, 'config.ini')
# rename column in dataframe
twitter_info_sen = twitter_info_sen.rename(columns={'name': 'twitter_name'})
# join official information about senators and twitter account
twitter_sen = pd.concat([senatori, twitter_info_sen],
                        axis=1, join="inner").drop(columns=['deputy'])
# select relevant columns
twitter_sen = twitter_sen[['surname', 'name', 'name_surname', 'twitter_name',
                           'screen_name', 'followers_count', 'friends_count',
                           'statuses_count', 'gender', 'user_id', 'verified',
                           'parliamentary_group', 'chamber']]
# save as csv file
twitter_sen.to_csv('twitter_sen.csv')

### CONCATENATE DEPUTIES AND SENATORS DATASETS
twitter_par = pd.concat([twitter_dep, twitter_sen], axis=0, ignore_index=True)
twitter_par.to_csv('twitter_depsen.csv')


### CONSIDER ONLY VERIFIED ACCOUNT
twitter_veracc = twitter_par[twitter_par['verified'] == True]
# Parties with number of verified account parliamentarians greater than 15
twitter_veracc = twitter_veracc[twitter_veracc['parliamentary_group'].isin(
    ['Partito Democratico', 'Lega', 'Movimento 5 Stelle', 'Azione - Italia Viva', "Fratelli d'Italia"])]

# Fix data about sen.Manca (homonym journalist with verified account)
twitter_veracc.loc[twitter_veracc['surname']
                   == 'Manca', ['screen_name']] = 'mancaimola'
twitter_veracc.loc[twitter_veracc['surname']
                   == 'Manca', ['followers_count']] = 1531
twitter_veracc.loc[twitter_veracc['surname']
                   == 'Manca', ['friends_count']] = 2262
twitter_veracc.loc[twitter_veracc['surname']
                   == 'Manca', ['statuses_count']] = 545
twitter_veracc.loc[twitter_veracc['surname']
                   == 'Manca', ['user_id']] = 897264492

# ministery account for sen. Bongiorno, Calderoli / on. Porta (homonym)
twitter_veracc.drop([164, 577, 590], axis=0, inplace=True)

twitter_veracc['surname'] = twitter_veracc.surname.str.title()
twitter_veracc['name'] = twitter_veracc.name.str.title()
twitter_veracc = twitter_veracc.sort_values('surname')

# This final dataset is the one to be used in the following steps of data collection. 
twitter_veracc.to_csv('twitter_veracc.csv')
