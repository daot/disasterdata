import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import sqlite3

conn = sqlite3.connect("../disasterdata/labeling/Database/posts-tornado.db")

cursor = conn.cursor()
cursor.execute("""SELECT id, SUBSTR(id, -13, 13) as post_id, sentiment from posts;""")

dataset = cursor.fetchall()
#print(dataset)

df = pd.DataFrame(dataset, columns = ['ID', 'PostID', 'Sentiment'])
#print(df)

g = sb.lineplot(data=df, x = "PostID", y = "Sentiment")
plt.xticks(rotation = 50)
plt.subplots_adjust(bottom = 0.33)
plt.show()



