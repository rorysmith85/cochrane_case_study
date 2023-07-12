import streamlit as st
import pandas as pd
import numpy as np
import json
import streamlit.components.v1 as components
import altair as alt
import networkx as nx
from pyvis.network import Network
from streamlit.components.v1 import html
import matplotlib.cm as cm
import re
from stvis import pv_static
from collections import defaultdict


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

path = "/Users/rorysmith/Desktop/cochrane_app/"

def create_stance_dataframes(df):
	stances = ['neutral', 'misleading', 'nuanced_accurate']

	df = df[df.notes.isna()]

	df = df[df.day >= "2023-01-29"]

	stance_dataframes = {}

	for stance in stances:
		stance_df = df[df['stance'] == stance]
		stance_df = stance_df.sort_values(by='day', ascending=True)
		# cumsum both retweets and impressions
		stance_df['retweets_cumulative'] = stance_df.retweets.cumsum()
		stance_df['impressions_cumulative'] = stance_df.impressions.cumsum()

		stance_dataframes[stance] = stance_df

	return stance_dataframes

def select_size(y_axis):
	if y_axis == "retweets_cumulative":
		return "retweets"
	else:
		return "impressions"

def scatter(df):
	df_dict = create_stance_dataframes(df)

	df_accurate = df_dict['nuanced_accurate'].copy()
	df_accurate['label'] = 'Accurate'

	df_misleading = df_dict['misleading'].copy()
	df_misleading['label'] = 'Misleading'

	combined_df = pd.concat([df_accurate, df_misleading], ignore_index=True)

	color_scale = alt.Scale(
		domain=["Accurate", "Misleading"],
		range=["#32CD32", "#FF7F7F"]
	)


	# Create the combined chart
	combined_chart = alt.Chart(combined_df, width=1200, height=700).mark_circle().encode(
		x="day:T",
		y=alt.Y(f'{y_axis}:Q', axis=alt.Axis(title=y_axis.capitalize())),
		size=alt.Size(f'{select_size(y_axis)}:Q', legend=None),
		tooltip=['link:N', f'{select_size(y_axis)}:Q', 'day:T'],
		href='link',
		color=alt.Color('label:N', scale=color_scale, legend=alt.Legend(title="Stances"))
	).interactive()


	combined_chart['usermeta'] = {
		"embedOptions": {
			'loader': {'target': '_blank'}
		}
	}

# 	combined_chart = combined_chart.properties(
#     autosize=alt.AutoSizeParams(
#         type='fit',
#         contains='padding'
#     )
# )

	chart_container = st.container()

	# Display the centered chart in Streamlit using the container
	with chart_container:
		st.write(
			"""
			<style>
				.element-container {
					display: flex;
					justify-content: center;
				}
			</style>
			""",
			unsafe_allow_html=True,
		)
		# st.altair_chart(scatter(news_coverage, stances))

		return st.altair_chart(combined_chart)

def create_stance_dataframes_youtube(df):
	stances = ['misleading', 'nuanced_accurate']

	df = df[df.day >= "2023-01-29"]

	stance_dataframes = {}
	
	for stance in stances:
		stance_df = df[df['stance'] == stance]
		stance_df = stance_df.sort_values(by='day', ascending=True)
		# cumsum both retweets and impressions
		stance_df['views_cumulative'] = stance_df.views.cumsum()

		stance_dataframes[stance] = stance_df

	return stance_dataframes


def scatter_youtube(df):
	df_dict = create_stance_dataframes_youtube(df)

	df_accurate = df_dict['nuanced_accurate'].copy()
	df_accurate['label'] = 'Accurate'

	df_misleading = df_dict['misleading'].copy()
	df_misleading['label'] = 'Misleading'

	combined_df = pd.concat([df_accurate, df_misleading], ignore_index=True)

	color_scale = alt.Scale(
		domain=["Accurate", "Misleading"],
		range=["#32CD32", "#FF7F7F"]
	)


	# Create the combined chart
	combined_chart = alt.Chart(combined_df, width=1200, height=700).mark_circle().encode(
		x="day:T",
		y="views_cumulative:Q",
		size=alt.Size("views:Q", legend=None),
		tooltip=['channel_title:N','link:N', "views:Q", 'day:T'],
		href='link',
		color=alt.Color('label:N', scale=color_scale, legend=alt.Legend(title="Stances"))
	).interactive()


	combined_chart['usermeta'] = {
		"embedOptions": {
			'loader': {'target': '_blank'}
		}
	}

	return st.altair_chart(combined_chart)


def create_stance_dataframes_facebook(df):
	stances = ['misleading', 'nuanced_accurate']

	df = df[df.day >= "2023-01-29"]

	stance_dataframes = {}
	
	for stance in stances:
		stance_df = df[df['stance'] == stance]
		stance_df = stance_df.sort_values(by='day', ascending=True)
		# cumsum both retweets and impressions
		stance_df['interactions_cumulative'] = stance_df.interactions.cumsum()

		stance_dataframes[stance] = stance_df

	return stance_dataframes


def scatter_facebook(df):
	df_dict = create_stance_dataframes_facebook(df)

	df_accurate = df_dict['nuanced_accurate'].copy()
	df_accurate['label'] = 'Accurate'

	df_misleading = df_dict['misleading'].copy()
	df_misleading['label'] = 'Misleading'

	combined_df = pd.concat([df_accurate, df_misleading], ignore_index=True)

	color_scale = alt.Scale(
		domain=["Accurate", "Misleading"],
		range=["#32CD32", "#FF7F7F"]
	)


	tooltip_list = ['link:N', "interactions:Q", 'day:T']

	# Check if 'name' column exists in the DataFrame
	if 'name' in combined_df.columns:
		tooltip_list.insert(0, 'name:N')

	# Create the combined chart
	combined_chart = alt.Chart(combined_df, width=1200, height=700).mark_circle().encode(
		x="day:T",
		y="interactions_cumulative:Q",
		size=alt.Size("interactions:Q", legend=None),
		tooltip=tooltip_list,
		href='link',
		color=alt.Color('label:N', scale=color_scale, legend=alt.Legend(title="Stances"))
	).interactive()


	combined_chart['usermeta'] = {
		"embedOptions": {
			'loader': {'target': '_blank'}
		}
	}

	return st.altair_chart(combined_chart)

content_column_1 = st.columns((1, 2, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_1:
	st.title('Masking the Truth: How a Cochrane Study Got Entangled in a Web of Misinformation')
	st.header('A recent Cochrane meta-analysis examining the efficacy of masks in protecting against COVID-19 has become a focal point for misinformation and manipulation, with\
	its findings taken out of context by anti-maskers and right-wing media outlets. This investigative piece traces the journey of the study from its publication to its misinterpretation\
	and distortion and the subsequent spread of this content online.')
	st.write("The COVID-19 pandemic has generated an unprecedented volume of scientific research, making it difficult for the public and even experts to differentiate between\
	credible sources and manipulated or out-of-context findings. In today's world of constant information overload, the misinterpretation and hijacking of a Cochrane study on\
	mask efficacy exemplifies how easily academic research can be misinterpreted and twisted to fit the beliefs and narratives of motivated communities.")
	st.write("The recent Cochrane study on masks exemplifies the ease with which findings can be misinterpreted, misleading content can spread and the challenges of providing access to\
	accurate information in today's complex information landscape")
	st.write("As the study's manipulation journey unfolds – from Substack and German media to Zero Hedge and a misleading New York Times op-ed – it reveals the shortcomings of\
	platforms like Twitter, YouTube, and Substack in ensuring access to accurate information, how corrections by both academic journals and media are relatively ineffective against\
	the onslaught of misleading and highly politicized content, and how the once-revered gatekeepers of knowledge - academic journals - are increasingly weaponized.")
	st.write("As more studies and preprints continue to be published, and where issues as seemingly innocuous as mask-wearing are highly politicized,\
	the risk of academic papers being taken out of context and disseminated across social media and mainstream news will continue to be a threat.")


	st.subheader('Tracking the media spread on Twitter')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Twitter.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	impressions or retweets they have received — the larger the node, the more impressions or retweets. The x axis represents the days between January 29 and April 2023, and the\
	y axis is the cumulative amount of impressions or retweets.")
	st.write("As you can see, media stories that misinterpreted or misleadingly portrayed the findings of the Cochrane study far outpaced (in terms of impressions,\
	retweets, and number of stories) media stories that accurately depicted the findings of the study. Using Meltwater and scraping Altmetric, we found 152 news stories\
	published between January 29 and April 1, 2023 addressing the the Cochrane study. Of these, 70% were misleading.")
	y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='news_stories')

news_stories = pd.read_csv(path + "news_stories_final_april26.csv")


scatter(news_stories)

content_column_1_point_5 = st.columns((1, 2.7, 1))[1]
with content_column_1_point_5:
	st.subheader('Tracking the media spread on Facebook')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Facebook.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	interactions they have received — the larger the node, the more interactions the story received on Facebook. The x axis represents the days between January 29 and April 1, 2023, and the\
	y axis is the cumulative amount of interactions.")

news_stories_facebook = pd.read_csv(path + 'aggregate_facebook.csv')

scatter_facebook(news_stories_facebook)

content_column_8 = st.columns((1, 2.7, 1))[1]
with content_column_8:
	st.subheader('Tracking the spread on Facebook')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Facebook.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	interactions they have received — the larger the node, the more interactions the story received on Facebook. The x axis represents the days between January 29 and April 1, 2023, and the\
	y axis is the cumulative amount of interactions.")

facebook_top_posts = pd.read_csv(path + 'facebook_top_80_cochrane.csv')

scatter_facebook(facebook_top_posts)

# Add a subheader and another text paragraph under the second section followed by scatter plot
content_column_2 = st.columns((1, 2.7, 1))[1]
with content_column_2:
	st.subheader('Top Tweets talking about Cochrane study')
	st.write("This scatterplot chronologically captures the top 1 percent of tweets (based on retweets) discussing the Cochrane study. While these tweets make up 1%\
	of all the tweets in the dataset, they account for 80 percent of the retweets.")
	y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='tweets')

top_tweets = pd.read_csv(path + '99th_percentile_tweets_april27.csv')

# y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='tweets')

scatter(top_tweets)


st.subheader('Nytimes articles')
st.write('This is a paragraph of text in section 2.')


def create_network(df):
	G = nx.Graph()

	# Create dictionaries to store all tweets and cumulative retweets for each username
	tweets_by_username = {}
	retweets_by_username = {}

	for index, row in nyt.iterrows():
		username = row['username']
		retweets = row['retweets']
		tweet = row['tweet']

		if username in tweets_by_username:
			tweets_by_username[username].append(tweet)
			retweets_by_username[username] += retweets
		else:
			tweets_by_username[username] = [tweet]
			retweets_by_username[username] = retweets

		G.add_node(username)
		G.add_edge(username, row['original_link'])

	net = Network(height='700px', width='1200px', notebook=True, bgcolor='#222222', font_color='white')


	net.from_nx(G)
	net.barnes_hut(overlap=1)
	net.repulsion(node_distance=800, central_gravity=0.01, spring_length=150)

	partition = community_louvain.best_partition(G)
	unique_communities = len(set(partition.values()))
	color_mapping = {0: "#32CD32", 1: "#FF7F7F"}

	for node in net.nodes:
		community_id = partition[node['id']]
		node['color'] = color_mapping[community_id]
		username = node['id']
		node['size'] = retweets_by_username.get(username, 0) / 10
		all_tweets = tweets_by_username.get(username, [])
		formatted_tweets = "<br>".join([f'<a href="{t}" target="_blank">{t}</a>' for t in all_tweets])
		node['title'] = f"Username: {username}<br>{formatted_tweets}"
		
			

	return net

nyt = pd.read_csv(path + 'nytimes_articles.csv')

# Create the network using the create_network function
net = create_network(nyt)

# pv_static(net)

# In the Streamlit app, display the HTML file with the network visualization
content_column_2 = st.columns((1, 2.3, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_2:
	st.title("Network Visualization")
	st.markdown("This is a network visualization of the nytimes pieces:")

# net.save_graph(f'{path}/nytimes_graph.html')

HtmlFile = open(f'{path}/nytimes_graph.html', 'r', encoding='utf-8')

html(HtmlFile.read(), height=900, width=1000)





content_column_3 = st.columns((1, 2.3, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_3:

	st.title("Entire network Visualization")
	st.markdown("This is a network visualization of the nytimes pieces:")


# load the two dataframes needed for the network viz
color_code = pd.read_csv(f'{path}color_code_misleading.csv')
tweets_stance = pd.read_csv(f'{path}top_80_percent_full_links_tweets_network_data.csv')

G = nx.DiGraph()

accuracy_ratio_dict = color_code.set_index('username')['accuracy_ratio'].to_dict()
color_mapping = {"misleading": "#FF7F7F", "nuanced_accurate": "#32CD32", "neutral":"grey"}

links_by_username = defaultdict(set)

# Create dictionaries to store all tweets and cumulative retweets for each username
tweets_by_username = {}
retweets_by_username = {}

for index, row in tweets_stance.iterrows():
	username = row['username']
	retweets = row['retweets']
	tweet = row['link']
	link = row['original_link']
	
	links_by_username[username].add(link)

	if username in tweets_by_username:
		tweets_by_username[username].append(tweet)
		retweets_by_username[username] += retweets
	else:
		tweets_by_username[username] = [tweet]
		retweets_by_username[username] = retweets

	G.add_node(username)
	G.add_edge(username, link)

net_2 = Network(height='700px', width='100%', notebook=True, bgcolor='#222222', font_color='white')
# net.repulsion()

net_2.from_nx(G)
net_2.barnes_hut(overlap=1)
net_2.repulsion(node_distance=800, central_gravity=0.01, spring_length=150)

		
for node in net_2.nodes:
	username = node['id']
	unique_links_count = len(links_by_username.get(username, set()))
	node['size'] = unique_links_count * 30
	all_tweets = tweets_by_username.get(username, [])
	formatted_tweets = "<br>".join([f'<a href="{t}" target="_blank">{t}</a>' for t in all_tweets])
	node['title'] = f"Username: {username}<br>{formatted_tweets}"
	
#     # Set the node color based on the accuracy_ratio value
	accuracy_ratio = accuracy_ratio_dict.get(username)
	if accuracy_ratio:
		node['color'] = color_mapping[accuracy_ratio]
		
for edge in net_2.edges:
	source_node_color = net_2.get_node(edge['from']).get('color', '#0000FF')
	print(edge, source_node_color)
	edge['color'] = source_node_color


net_2.save_graph(f'{path}/full_links_graph.html')

HtmlFile2 = open(f'{path}/full_links_graph.html', 'r', encoding='utf-8')

html(HtmlFile2.read(), height=900, width=1000)


content_column_4 = st.columns((1, 2.7, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_4:
	st.title("YouTube Videos")
	st.markdown("YouTube Videos")

yt = pd.read_csv(path + 'cochrane_youtube_coded.csv')

# cleaning the csv file
yt = yt[~yt.stance.isna()]
yt['day'] = yt.publishedAt.apply(lambda x: pd.to_datetime(x))
yt = yt[['day','link', 'channelTitle', 'viewCount', 'stance']]
yt.columns = ['day','link', 'channel_title', 'views', 'stance']

scatter_youtube(yt)









