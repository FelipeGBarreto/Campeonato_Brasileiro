#Atualizado até 18/12/2021
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


# ## Bases de Dados

path = "/Users/felipebarreto/Documents/Projeto - Campeonato Brasileiro/Dados/"

df = pd.read_csv(path + "campeonato-brasileiro-estatisticas-full.csv", sep=";")
times = pd.read_csv(path + "campeonato-brasileiro-full.csv", sep=";")
estados = pd.read_csv(path + "estados.csv", sep=';', encoding='latin-1') ; estados.columns = ['estado','uf','regiao']
temporadas = pd.read_csv(path + "temporadas.csv", sep =';')


## Algumas funções necessárias ##

# transformar string em datetime
def to_time(df, col):
    df[col] = pd.to_datetime(df[col])

# transformação de uma variável em um inteiro
def to_int (df, col):
    df[col] = df[col].str.astype(int)

def str_to_float (df, col):
    df[col] = df[col].str.replace('%', '').astype(float)

# plot dos valores faltantes
def missing_map(df, size_x=15, size_y=5, color = 'Reds'):
    plt.figure(figsize=(size_x,size_y))
    plt.title(f"Valores Faltantes em {df.name}", fontweight = 'bold', fontsize = 15)
    ax = sns.heatmap(df.isna().sum().to_frame(), annot = True, fmt = 'd', cmap = color)
    ax.set_ylabel("Variáveis", fontsize=12)
    ax.set_xlabel('Quantidade Faltante', fontsize=12)

# função para transformar as observações em minúsculas
def to_lower(df, col):
    df[col] = df[col].str.lower()
    
# funções de agrupamento de dados
def agrup(df, col_group, col, func = sum):
    return(df.groupby(col_group)[[col]].apply(func, axis=0).reset_index().rename(columns={col_group:'time'}))

def agrup_c(df, col_group, col):
    return(df.groupby(col_group)[[col]].count().reset_index().rename(columns={col_group:'time'}))

# ordenando desc --> 1º linha
def df_ordem(df, col, asc=False):
    return(df.sort_values(by=[col], ascending=asc))[:1]


## Ajustes nos datasets ##

# Algumas transformações necessárias
to_time(times, 'Data')
times.Mandante = times.Mandante.replace('athletico-pr','athlético-pr')
times.Visitante = times.Visitante.replace('athletico-pr','athlético-pr')

for i in ['data_inicio', 'data_fim']:
    to_time(temporadas, i)

# colocando para minúsculas (ajuda nas duplicidades)
for i in ['Dia', 'Mandante', 'Visitante','Vencedor', 'Arena','Estado Mandante', 'Estado Visitante', 'Estado Vencedor']:
    to_lower(times, i)

for i in estados.columns:
    to_lower(estados, i)

# renomeando as colunas do dataset
rename_df = {
     'ID': 'id', 
     'Mandante': 'mandante',
     'Chutes': 'chutes', 
     'Chutes a gol': 'chutes_gol', 
     'Posse de bola': 'posse_bola', 
     'Passes': 'passes',
     'Precisão de passe': 'precisao_passes', 
     'Faltas': 'faltas', 
     'Cartões amarelos': 'cartoes_amarelos', 
     'Cartões vermelhos': 'cartoes_vermelhos',
     'Impedimentos': 'impedimentos', 
     'Escanteios': 'escanteios' 
}
df = df.rename(columns = rename_df)

rename_times = {
    'ID': 'id',
    'Rodada': 'rodada',
    'Data': 'data',
    'Horário':'horario',
    'Dia':'dia',
    'Mandante':'mandante',
    'Visitante':'visitante',
    'Vencedor':'vencedor',
    'Arena':'arena',
    'Mandante Placar':'mandante_placar',
    'Visitante Placar':'visitante_placar',
    'Estado Mandante':'estado_mandante',
    'Estado Visitante':'estado_visitante',
    'Estado Vencedor': 'estado_vencedor'
    }
times = times.rename(columns = rename_times)

# retirando o símbolo de % e transformando em float
for i in ['posse_bola','precisao_passes']:
    str_to_float(df, i)
    
# filtrando somente os josgos de 2003 em diante (pontos corridos) --> Temporadas de 2003 a 2020
times = times[(times.data >= '2003-03-29') & (times.data <= '2019-12-08')]

# definindo o perdedor
times['perdedor'] = np.array([0]*times.shape[0])
for i in range(times.shape[0]):
    if times.vencedor.iloc[i] == "-": times.perdedor.iloc[i] = "-"
    elif times.vencedor.iloc[i] == times.mandante.iloc[i]: times.perdedor.iloc[i] = times.visitante.iloc[i]
    elif times.vencedor.iloc[i] == times.visitante.iloc[i]: times.perdedor.iloc[i] = times.mandante.iloc[i]
    else: times.perdedor.iloc[i] = "-"

# turno do jogo
times['turno_dia'] = times.horario
times.loc[(pd.to_datetime(times.horario.str.replace("h",":")) >= '05:00:00'), "turno_dia"] = 'manhã'
times.loc[(pd.to_datetime(times.horario.str.replace("h",":")) >= '12:00:00'), "turno_dia"] = 'tarde'
times.loc[(pd.to_datetime(times.horario.str.replace("h",":")) >= '18:00:00'), "turno_dia"] = 'noite'

# saldo placar --> mandante como referência
times['saldo_placar'] = times.mandante_placar - times.visitante_placar

# pontos ganhos
times['pontos_mandante'] = np.array([0]*times.shape[0])
times['pontos_visitante'] = np.array([0]*times.shape[0])
for i in range(times.shape[0]):
    if times.saldo_placar.iloc[i] > 0: 
        times['pontos_mandante'].iloc[i] = 3 
        times['pontos_visitante'].iloc[i] = 0
    elif times.saldo_placar.iloc[i] == 0: 
        times['pontos_mandante'].iloc[i] = 1 
        times['pontos_visitante'].iloc[i] = 1
    else: 
        times['pontos_mandante'].iloc[i] = 0 
        times['pontos_visitante'].iloc[i] = 3
    
# Dando nomes aos datasets
df.name = 'df'; times.name = 'times'; estados.name = 'estados'

# verificando valores faltantes
missing_map(df, 15, 5)
missing_map(times, 15, 5, color="RdPu") 


times_todos = np.unique(
    np.concatenate([times.mandante.unique(), 
                    times.visitante.unique()]))

ufs = np.array(estados.uf)


## Acescentando uma coluna que representa a temporada que é de cada partida
times['temporada'] = times.data.dt.year
for i in range(times.shape[0]):
    for j in range(temporadas.shape[0]):
        if (times.data.iloc[i] >= temporadas.data_inicio.iloc[j]) and (times.data.iloc[i] <= temporadas.data_fim[j]):
             times['temporada'].iloc[i] =  temporadas.temporada.iloc[j]

## Ajustando os três jogos a mais de 2007 para 2008
for i in [3010,3011,3012]:
    times.loc[times.id == i, "temporada"] =  'temporada_2008'


# Funcao com o resumo geral dos times

def df_times(equipe = times_todos, temporada_escolhida=np.array(times.temporada.unique())):
    
    df = times[times.temporada.isin(temporada_escolhida)]
    
    #marcados
    gols_marcados = agrup(df, "mandante", "mandante_placar").merge(agrup(df, "visitante", "visitante_placar"), on='time', how='inner')
    gols_marcados['gols_marcados'] = gols_marcados['mandante_placar'] + gols_marcados['visitante_placar']

    #levados
    gols_levados = agrup(df, "visitante", "mandante_placar").merge(agrup(df, "mandante", "visitante_placar"), on='time', how='inner')
    gols_levados['gols_levados'] = gols_levados['mandante_placar'] + gols_levados['visitante_placar']

    #vitórias e derrotas
    vitorias_derrotas = agrup_c(df, "vencedor", "id").rename(columns={'id':'vitorias'}).merge(
                        agrup_c(df, "perdedor", "id").rename(columns={'id':'derrotas'}), on='time', how='outer')

    #empates
    empates = agrup_c(df[df.vencedor == '-'], "mandante", "id").merge(agrup_c(df[df.vencedor == '-'], "visitante", "id"), on='time', how='inner')
    empates['empates'] = empates.id_x + empates.id_y

    #pontos
    pontos = agrup(df, "mandante", "pontos_mandante").merge(agrup(df, "visitante", "pontos_visitante"), on='time', how='inner')
    pontos['pontos'] = pontos.pontos_mandante + pontos.pontos_visitante


    resumo_times = gols_marcados.merge(gols_levados, on='time', how='inner')                                .merge(vitorias_derrotas, on='time', how='inner')                                .merge(empates[['time','empates']], on='time', how='inner')                                .merge(pontos, on='time', how='inner')                                .rename(columns = {'mandante_placar_x':'marcou_como_mandante',
                                                   'visitante_placar_x':'marcou_como_visitante',
                                                   'mandante_placar_y':'levou_como_visitante',
                                                   'visitante_placar_y':'levou_como_mandante'})
    
    resumo_times['partidas_jogadas'] = resumo_times['vitorias'] + resumo_times['empates'] + resumo_times['derrotas']
    resumo_times['saldo_gols'] = resumo_times['gols_marcados'] - resumo_times['gols_levados']
    resumo_times = resumo_times.sort_values(by=['pontos'], ascending = False)                               .rename(columns = {'time':'Clube', 'partidas_jogadas':'PJ','vitorias':'VIT','empates':'E','derrotas':'DER','gols_marcados':'GP','gols_levados':'GC','saldo_gols':'SG'})                               .set_index('Clube').reset_index()
    
    resumo_times = resumo_times[resumo_times.Clube.isin(equipe)]
    
    return(resumo_times)

# funcao com o detalhamento do time ou da temporada
def classificacao():
    print(
         "---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n                   "
    "CAMPEONATO BRASILEIRO\n---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n")
    resp_clube = input("P: Deseja ver algum clube específico?\n> R: ").lower()
    if resp_clube in ("s","sim","y","yes"): 
        clube = np.array([input("P: Qual clube?\n> R:").lower()])
        print("\n>>> Classificação do {}\n".format(clube[0].title()))
    else: 
        clube = times_todos
        print("\n>>>Classificação de todos os times:\n")

    resp_temp = input("P: Alguma temporada específica?\n> R:").lower()
    if resp_temp in ("s","sim","y","yes"): 
        temp = np.array(['temporada_' + input("P: Qual temporada (ano)?\n> R:").lower()])
    else: temp = np.array(times.temporada.unique())

    # classificacao + resumo
    x = df_times(equipe=clube, temporada_escolhida=temp)[['Clube','PJ','VIT','E','DER','GP','GC','SG']]
    x.Clube = x.Clube.str.title()
    return(x)


print(">> ESTATÍSTICAS GERAIS:\n\n"      "- Maior vencedor de jogos do Brasileirão: {} com {} vitórias!\n"      "- Pior vencedor de jogos do Brasileirão: {} com {} vitórias!\n"      "- Maior perdedor: {}, com {} derrotas\n"      "- Melhor ataque: {}, com {} gols marcados\n"      "- Pior defesa: {}, com {} gols levados\n"      .format(
          df_ordem(df_times(), "VIT").Clube.iloc[0].title(), df_ordem(df_times(), "VIT").VIT.iloc[0],
          df_ordem(df_times(), "VIT", asc=True).Clube.iloc[0].title(), df_ordem(df_times(), "VIT", asc=True).VIT.iloc[0],
          df_ordem(df_times(), "DER").Clube.iloc[0].title(), df_ordem(df_times(), "DER").DER.iloc[0],
          df_ordem(df_times(), "GP").Clube.iloc[0].title(), df_ordem(df_times(), "GP").GP.iloc[0],
          df_ordem(df_times(), "GC").Clube.iloc[0].title(), df_ordem(df_times(), "GC").GC.iloc[0]
))

classificacao()

# #### Criando uma função para ver as estatísticas

def stats_team(time_escolhido):
    print("\n\n>>>   Algumas estatísticas sobre o time {}   <<<\n\n"
        "- Número de vitórias do time nas temporadas: {}\n"\
        "- Percentual de vitórias por temporada: {}%\n\n"\
        "- Número de empates do time nas temporadas: {}\n"\
        "- Percentual de empates por temporada: {}%\n\n"\
        "- Número de derrotas do time nas temporadas: {}\n"\
        "- Percentual de derrotas por temporada: {}%\n\n"\
        "- Temporadas dem que o time ficou na 1º divisão: {}\n"\
        "- De {} temporadas da Série A, participou de {} temporadas. Ou seja, de {}%\n\n"\
        .format(time_escolhido[0].title(), 
                df_times(equipe=time_escolhido).VIT.iloc[0],
                round((100*df_times(equipe=time_escolhido).VIT.iloc[0] / df_times(equipe=time_escolhido).PJ.iloc[0]), 2),
                df_times(equipe=time_escolhido).E.iloc[0],
                round((100*df_times(equipe=time_escolhido).E.iloc[0] / df_times(equipe=time_escolhido).PJ.iloc[0]), 2),
                df_times(equipe=time_escolhido).DER.iloc[0],
                round((100*df_times(equipe=time_escolhido).DER.iloc[0] / df_times(equipe=time_escolhido).PJ.iloc[0]), 2),
                times[(times.mandante == time_escolhido[0]) | (times.visitante == time_escolhido[0])].temporada.unique(),
                len(times.temporada.unique()), len(times[(times.mandante == time_escolhido[0]) | (times.visitante == time_escolhido[0])].temporada.unique()),
                ((100*len(times[(times.mandante == time_escolhido[0]) | (times.visitante == time_escolhido[0])].temporada.unique()) / len(times.temporada.unique())),2)
        ))


# #### Looping do resultado

# estatística sobre o time
print(
    "---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n                   "
    "AVALIAÇÃO DO SEU TIME!\n---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n")
time_escolhido = np.array([input("\nQual o time que deseja avaliar?\n>> Time: ").lower()])
assert time_escolhido in times_todos, f"Coloque um dos times que ja participaram do Brasileirão\n {sorted(times_todos)}"
print("\n............................................................")
stats_team(time_escolhido)                                      

# looping
continuar = input("---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n\n"
"Deseja ver outro time?\nResposta: ")
assert continuar in ("s","sim","S","Sim","yes","Yes","y","Y"), "Sim ou não!"
while continuar in ("s","sim","S","Sim","yes","Yes","y","Y"):
    time_escolhido = np.array([input("\nQual o time que deseja avaliar?\n>> Time: ").lower()])
    assert time_escolhido in times_todos, f"Coloque um dos times que já participaram do Brasileirão\n {sorted(times_todos)}"
    print("\n---.---.---.---.---.---.---.---.---.---.---.---.---.---.---")
    stats_team(time_escolhido)
    continuar = input("---*---*---*---*---*---*---*---*---*---*---*---*---*---*---\n\n"
    "Deseja ver outro time?\n\nResposta: ")
    assert continuar in ("s","sim","S","Sim","yes","Yes","y","Y"), "Sim ou não!"

