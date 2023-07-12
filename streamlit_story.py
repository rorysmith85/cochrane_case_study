import streamlit as st
import pandas as pd
import numpy as np
import json
import streamlit.components.v1 as components
import altair as alt
import networkx as nx
from pyvis.network import Network
from streamlit.components.v1 import html
import community as community_louvain
import matplotlib.cm as cm
import re
from collections import defaultdict


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# path = "/Users/rorysmith/Desktop/cochrane_app/"

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
	st.title('Masking the Truth: How a Cochrane Study Got Entangled in a Web of Misinterpretation')
	st.header('A Cochrane meta-analysis examining the efficacy of masks in protecting against Covid-19 became a focal point for misleading narratives.')
	st.write("The Covid-19 pandemic caused an explosion of new information, some based on scientific research that had received peer-review, some published immediately to help advance knowledge \
 	but without peer-review (pre-prints), and some information was based on little more than personal experience or conjecture.  The extraordinary amount of information made it very difficult for \
  	the public and even experts to differentiate between credible sources and manipulated or out-of-context findings.")
	st.write("In January 2023, a poorly worded abstract (later acknowledged by the authors themselve) associated with a review of the evidence about the efficacy of masking – s – was published by \
 	Cochrane, the gold-standard public health research organization in relation to a systematic review of the evidence around masking by. Cochrane — a misstep \
  	[acknowledged by Cochrane itself](https://www.cochrane.org/news/statement-physical-interventions-interrupt-or-reduce-spread-respiratory-viruses-review) — This case study exemplifies how easily academic research can be taken out of context and manipulated to fit the \
   	pre-existing beliefs and narratives of different communities online, and why the ways in which research is communicated, particularly the methodologies used and the conclusions \
    	that can be drawn, are so fundamental.", unsafe_allow_html=True)
	st.write("A thorough reading by a researcher with extensive methodological expertise would likely have led to accurate conclusions. However, the poorly worded abstract allowed individuals, \
 	who may have lacked the time or the appropriate methodological training to delve deeper, to draw inaccurate and potentially dangerous conclusions. This didn’t lead to obscure debates at public \
  	health academic conferences — it drove mainstream conversations based on the false assertion that masks don’t work.")
	st.write("The original review was published on January 30, 2023, but almost immediately news stories and headlines <a href=https://www.washingtonexaminer.com/restoring-america/faith-freedom-self-reliance/gold-standard-scientific-study-finds-masks-are-useless-against-covid> \
 	misrepresenting the findings</a> and inaccurately claiming that “masks don’t work” jumped from Substack to ZeroHedge, the Washington Free Beacon and Fox News while simultaneously moving at speed \
  	across Twitter and Facebook. On February 21, three weeks after the study’s publication, <a href=https://www.nytimes.com/2023/02/21/opinion/do-mask-mandates-work.html>an op-ed in the New York Times \
   	by Bret Stephens</a> accelerated the spread of misleading claims surrounding the study, declaring in its headline that “the mask mandates did nothing.”  Various fact-checks, \
    	<a href=https://www.cochrane.org/news/statement-physical-interventions-interrupt-or-reduce-spread-respiratory-viruses-review> a statement by Cochrane<a/>, which underlined how the results of the \
     	study were inconclusive, as well as <a href=https://www.nytimes.com/2023/03/10/opinion/masks-work-cochrane-study.html>another New York Times op-ed<a/> discussing that statement were issued but they \
      	had little impact on the spread of misleading content on Facebook and Twitter.", unsafe_allow_html=True)
       	st.write("Nonetheless, by the time the statement and second op-ed were published, inaccurate versions of the study findings had received at least 27 million impressions on Twitter, several million \
	views on YouTube, and tens of thousands of interactions on Facebook across multiple languages.")
 	st.write("In this case study, we track the spread of content, including media reports, related to the findings of the Cochrane study on Twitter, Facebook and YouTube. It shows how poorly worded \
  	communications products can result in misleading coverage. In our networked information ecosystem, clarifying statements or corrections stand little chance of being effective, particularly on \
   	issues that are politicized. And it raises questions about the need for stringent fact checking, even for op-ed pages, as reputable news sources have an outsized role in amplifying the spread of \
    	information.)
     	st.write("It also underlines how academic journals and research publications — the perennial gatekeepers of knowledge — no longer have any room for missteps or errors. On politicized topics \
      	(and unfortunately viruses, masks and vaccines now fall into this category), “trusted” sources of information are increasingly being weaponized by those looking for “credible sources” to support \
       	outlandish claims. The idea that the gold-standard institution for publishing systematic reviews on health care and health policy, Cochrane, was claiming any type of ambiguity around the \
	effectiveness of masks was so surprising. And among reporters without a solid understanding of the limitations of Randomly Controlled Trials (RCTs), the suggestion in the faulty abstract — that \
 	there was insufficient evidence to support a conclusion that masks work — was understood by too many as "masks don't work.")
  	st.write("As more studies and preprints are published and disseminated across social media — where catchy headlines and cherry-picked evidence that aligns with certain views get clicks and \
   	traffic — the risk of academic papers being taken out of context, misinterpreted, and then taken as fact will continue to be a major obstacle to building consensus around public health efforts.)



	st.subheader('Tracking the media spread on Twitter')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Twitter.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	impressions or retweets they have received — the larger the node, the more impressions or retweets. The x axis represents the days between January 29 and April 2023, and the\
	y axis is the cumulative amount of impressions or retweets.")
	st.write("As you can see, media stories that misinterpreted or misleadingly portrayed the findings of the Cochrane study far outpaced (in terms of impressions,\
	retweets, and number of stories) media stories that accurately depicted the findings of the study. Using Meltwater and scraping Altmetric, we found 152 news stories\
	published between January 29 and April 1, 2023 addressing the the Cochrane study. Of these, 70% were misleading.")
	y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='news_stories')

news_stories = pd.read_csv("news_stories_final_april26.csv")


scatter(news_stories)

content_column_1_point_5 = st.columns((1, 2.7, 1))[1]
with content_column_1_point_5:
	st.subheader('Tracking the media spread on Facebook')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Facebook.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	interactions they have received — the larger the node, the more interactions the story received on Facebook. The x axis represents the days between January 29 and April 1, 2023, and the\
	y axis is the cumulative amount of interactions.")

news_stories_facebook = pd.read_csv('aggregate_facebook.csv')

scatter_facebook(news_stories_facebook)

content_column_8 = st.columns((1, 2.7, 1))[1]
with content_column_8:
	st.subheader('Tracking the spread on Facebook')
	st.write("The scatterplot chronologically shows how different media outlets reported on the Cochrane study and the amount of engagement they received on Facebook.\
	You can hover over the nodes in the plot to see more details and you can click on the link in the nodes to open the tweet. The nodes are sized based on the number of\
	interactions they have received — the larger the node, the more interactions the story received on Facebook. The x axis represents the days between January 29 and April 1, 2023, and the\
	y axis is the cumulative amount of interactions.")

facebook_top_posts = pd.read_csv('facebook_top_80_cochrane.csv')

scatter_facebook(facebook_top_posts)

# Add a subheader and another text paragraph under the second section followed by scatter plot
content_column_2 = st.columns((1, 2.7, 1))[1]
with content_column_2:
	st.subheader('Top Tweets talking about Cochrane study')
	st.write("This scatterplot chronologically captures the top 1 percent of tweets (based on retweets) discussing the Cochrane study. While these tweets make up 1%\
	of all the tweets in the dataset, they account for 80 percent of the retweets.")
	y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='tweets')

top_tweets = pd.read_csv( '99th_percentile_tweets_april27.csv')

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

# nyt = pd.read_csv( 'nytimes_articles.csv')

# # Create the network using the create_network function
# net = create_network(nyt)

# In the Streamlit app, display the HTML file with the network visualization
content_column_2 = st.columns((1, 2.3, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_2:
	st.title("Network Visualization")
	st.markdown("This is a network visualization of the nytimes pieces:")

# net.save_graph(f'{path}/nytimes_graph.html')

HtmlFile = open('nytimes_graph.html', 'r', encoding='utf-8')

html(HtmlFile.read(), height=900, width=1000)





content_column_3 = st.columns((1, 2.3, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_3:

	st.title("Entire network Visualization")
	st.markdown("This is a network visualization of the nytimes pieces:")


# load the two dataframes needed for the network viz
color_code = pd.read_csv('color_code_misleading.csv')
tweets_stance = pd.read_csv('top_80_percent_full_links_tweets_network_data.csv')

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


net_2.save_graph('full_links_graph.html')

HtmlFile2 = open('full_links_graph.html', 'r', encoding='utf-8')

html(HtmlFile2.read(), height=900, width=1000)


content_column_4 = st.columns((1, 2.7, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_4:
	st.title("YouTube Videos")
	st.markdown("YouTube Videos")

yt = pd.read_csv( 'cochrane_youtube_coded.csv')

# cleaning the csv file
yt = yt[~yt.stance.isna()]
yt['day'] = yt.publishedAt.apply(lambda x: pd.to_datetime(x))
yt = yt[['day','link', 'channelTitle', 'viewCount', 'stance']]
yt.columns = ['day','link', 'channel_title', 'views', 'stance']

scatter_youtube(yt)









