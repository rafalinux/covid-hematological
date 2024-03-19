# Libraries to import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.dates import MonthLocator, DateFormatter
from datetime import datetime
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import seaborn as sns
#from statsmodels.tsa.api import SimpleExpSmoothing

# CSV file to import and some cleaning and preprocessing
pacientes = pd.read_csv("/home/rafoide/Python_Projects/COVID_Hemato/pacientes_COVID_Hematologicos_redux_2020-2022.csv")
pacientes["Fecha.de.Ingreso"] = pd.to_datetime(pacientes["Fecha.de.Ingreso"])
pacientes["Fecha.de.Fin.Contacto"] = pd.to_datetime(pacientes["Fecha.de.Fin.Contacto"])
pacientes["NeoplasiaHematologica"] = np.where((pacientes["LinfomaHodgkin"] == "yes") |
                                             (pacientes["LinfomaBFolicular"] == "yes") |
                                             (pacientes["LinfomaTNK"] == "yes") |
                                             (pacientes["Mieloma"] == "yes") |
                                             (pacientes["Leucemia"] == "yes") |
                                             (pacientes["Mieloproliferativo"] == "yes"), "yes", "no")
pacientes_hemato = pacientes[pacientes["NeoplasiaHematologica"] == "yes"]

# This is the first derived dataframe.
ingresos = pacientes_hemato["Fecha.de.Ingreso"].value_counts().reset_index().rename(columns={"index": "Var1", "Fecha.de.Ingreso": "Freq"})
ingresos["Var1"] = pd.to_datetime(ingresos["Var1"], format='%Y-%m-%d')
# las fechas están desordenadas, hay que ordenarlas en ascendente
ingresos = ingresos.sort_values(by='Var1')
#ingresos.sort_values(by='Var1', inplace=True) # esto es para modificar el dataframe original
rolling_average = ingresos["Freq"].rolling(window=7).mean()
rolling_average = rolling_average.fillna(0)
ingresos["moving_average"] = rolling_average
ingresos["acumulados"] = ingresos["Freq"].cumsum()

# Since pacientes_hemato.csv cannot be available (it cannot be published, either),
# we uploaded the file ingresos.csv.
# ingresos.csv is available within this repository and can be imported as follows:
# ingresos = pd.read_csv("ingresos.csv")

min_date = datetime.strptime("2020-02-12", "%Y-%m-%d")
max_date = datetime.strptime("2022-12-31", "%Y-%m-%d")

###########################################
# DAILY ADMISSIONS: PLOT and SCATTER PLOT 
###########################################
# Create figure and plot space
fig, ax = plt.subplots(figsize=(12, 10))

# Add x-axis and y-axis
ax.plot(ingresos['Var1'],
        ingresos['moving_average'],
        color='red', label="7-day moving average")

ax.scatter(ingresos['Var1'],
        ingresos['Freq'],
        color='lightsteelblue', label="Admissions")
 
# Set title and labels for axes
ax.set(#xlabel="Date",
       ylabel="Hospital admissions",
       title="Patients with hematologic malignancy (2020-2022)")
#fig.suptitle('Patients with hematologic malignancy (2020-2022)')
#fig.suptitle('Example Plot')
plt.suptitle('            Daily admissions due to COVID-19')
ax.grid(True)

# Format the x-axis for dates (label formatting, rotation)
fig.autofmt_xdate(rotation=45)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%B-%Y')) #esto pone la fecha mejor
fig.tight_layout()

# add vertical line
ax.vlines(x=[datetime(2021, 1, 1)], color='teal', ymin=0, ymax=120, ls='--', label='Year 2021')
ax.vlines(x=[datetime(2022, 1, 1)], color='teal', ymin=0, ymax=120, ls='--', label='Year 2022')

ax.legend(loc='upper right')  # Add a legend.

# function savefig() should be called BEFORE show() to save the image on disk:
#plt.savefig('admissions.png', facecolor='white')
plt.show()

# Temporary dataframe for the next Figure
ingresos0 = ingresos[["Var1", "Freq"]]
ingresos1 = ingresos0.groupby(ingresos['Var1'].dt.to_period('M')).sum()
ingresos1 = ingresos1.resample('M').asfreq().fillna(0)

###########################################
# BARPLOT of ADMISSIONS 
###########################################
# Create figure and plot space
plt.rcParams['axes.titlesize'] = 10
ax = ingresos1.plot(kind='bar', 
                  figsize=(12, 10), 
                  width=0.8, # size of bars
                  #color = "lightseagreen",
                  color='lightsteelblue',
                  legend=False)
# Set title and labels for axes
ax.title.set_size(40)
ax.set(xlabel="",
       ylabel="Hospitalizations",
       title="Patients with hematologic malignancy (2020-2022) \nMonthly admissions due to COVID-19") # \n is a line break

# Format the x-axis for dates (label formatting, rotation)
plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
ax.xaxis.set_tick_params(labelsize=8)
ax.yaxis.set_tick_params(labelsize=8)

# Format dates
ticklabels = ['']*len(ingresos1.index)
ticklabels[::2] = [item.strftime('%B-%Y') for item in ingresos1.index[::2]] # one tick every two dates
ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
plt.gcf().autofmt_xdate()

# function savefig() should be called BEFORE show() to save the image on disk:
# plt.savefig('barplot_admissions.png', facecolor='white')
plt.show()

# The defaults can be restored using
plt.rcParams.update(plt.rcParamsDefault)

###########################################
# BARPLOT of DEATHS
###########################################

dataframe_exitus = pacientes_hemato[pacientes_hemato['Tipo.Alta'] == 4]
exitus = pd.DataFrame(dataframe_exitus['Fecha.de.Ingreso'].value_counts()).reset_index()
exitus.columns = ['Var1', 'Freq']
exitus['Var1'] = pd.to_datetime(exitus['Var1'], format="%Y-%m-%d")
exitus['Month'] = pd.to_datetime(exitus['Var1']).dt.to_period('M')
exitus = exitus.sort_values(by='Var1')
# Adding the column "Month"
exitus1 = exitus.groupby(exitus['Var1'].dt.to_period('M')).sum()
exitus1 = exitus1.resample('M').asfreq().fillna(0)

# To create dataframes "exitus" and "exitus1" one can need the dataframe "pacientes_hemato",
# which we cannot provide. But we can provide "exitus.csv" and "exitus1.csv".
# exitus = pd.read_csv("exitus.csv")
# exitus1 = pd.read_csv("exitus1.csv")

###################################
# First approach to plot mortality:
###################################
# Create figure and plot space
fig, ax = plt.subplots(figsize=(12, 10))

# The barplot
ax = sns.barplot(data=exitus, x='Month', y='Freq',
            estimator=sum, errorbar=None,
            color = "lightseagreen",
            saturation = 0.75)

# Set title and labels for axes
ax.set(xlabel="",
       ylabel="In-hospital deaths",
       title="Patients with hematologic malignancy (2020-2022)")
plt.suptitle('          Monthly mortality due to COVID-19')
ax.grid(True)

# Format the x-axis for dates (label formatting, rotation)
fig.autofmt_xdate(rotation=45)
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%B-%Y')) #esto pone la fecha mejor
fig.tight_layout()

plt.show()

####################################
# Second approach to plot mortality:
####################################
# Create figure and plot space
plt.rcParams['axes.titlesize'] = 10
ax = exitus1.plot(kind='bar', 
                  figsize=(12, 10), 
                  width=0.8, # tamaño de las columnas
                  color = "lightseagreen",
                  #color='lightsteelblue',
                  legend=False)
# Set title and labels for axes
ax.title.set_size(40)
ax.set(xlabel="",
       ylabel="In-hospital deaths",
       title="Patients with hematologic malignancy (2020-2022) \nMonthly mortality due to COVID-19") #

# Format the x-axis for dates (label formatting, rotation)
plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
ax.xaxis.set_tick_params(labelsize=8)
ax.yaxis.set_tick_params(labelsize=8)

# Format of dates
ticklabels = ['']*len(exitus1.index)
ticklabels[::2] = [item.strftime('%B-%Y') for item in exitus1.index[::2]]
ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
plt.gcf().autofmt_xdate()

# la función savefig() debe invocarse ANTES que show()
#plt.savefig('mortality.png', facecolor='white')
plt.show()

# The defaults can be restored using
plt.rcParams.update(plt.rcParamsDefault)

##############################
# POBLATIONAL PYRAMID
##############################
# Import and preprocess the dataset
pyramid = pd.read_csv("piramide.csv")
# convert male counts to negative
pyramid.loc[pyramid.sexo.eq('Men'), 'poblacion'] = pyramid.poblacion.mul(-1) #cambio los valores de Men a negativos
# reorder "rango" to non-ascending
pyramid.sort_values('rango',inplace=True, ascending=False)

# Plot the pyramid
plt.rcParams['axes.titlesize'] = 10
# plot
plt.figure(figsize=(12,10))
ax = sns.barplot(data=pyramid, x='poblacion',y='rango',
            hue='sexo',orient='horizontal', 
            #color = 'lightsteelblue',
            palette = 'Blues',
            dodge=False)

# Decorations
ax.set(xlabel="",
       ylabel="Age range",
       title="Hospitalized patients with hematologic malignancy and COVID-19")
plt.yticks(fontsize=10)

plt.legend()

#turn the negative values on the x axis to positive
ax.set_xticklabels([int(max(x, -x)) for x in ax.get_xticks()]) 

# la función savefig() debe invocarse ANTES que show()
#plt.savefig('pyramid_python.png', facecolor='white')
plt.show()
plt.rcParams.update(plt.rcParamsDefault)