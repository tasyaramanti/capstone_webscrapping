from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'table-responsive'})

row = table.find_all('tr')
row_length = len(row)

kurs = [] #initiating a list 

for i in range(row_length):
    #to get date column
    tanggal = table.find_all('tr')[i].find_all('td')[0].text
    
    #to get the exchange rate amount without additional text
    kurs_harian = table.find_all('tr')[i].find_all('td')[2].text[:-4]
    
    kurs.append((tanggal, kurs_harian)) 
    #scrapping process

kurs = kurs[::-1]

#change into dataframe
df = pd.DataFrame(kurs, columns = ('tanggal', 'kurs_harian'))

#insert data wrangling here
df['tanggal'] = df['tanggal'].astype('datetime64')
df['kurs_harian'] = df['kurs_harian'].str.replace(",","").astype('float64')
df = df.set_index('tanggal')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{round(df["kurs_harian"].mean(), 2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (15,7)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)