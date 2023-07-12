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
  	across Twitter and Facebook. On February 21, three weeks after the study’s publication, [an op-ed in the New York Times \
   	by Bret Stephens](https://www.nytimes.com/2023/02/21/opinion/do-mask-mandates-work.html) accelerated the spread of misleading claims surrounding the study, declaring in its headline that “the mask mandates did nothing.”  Various fact-checks, \
    	[a statement by Cochrane](https://www.cochrane.org/news/statement-physical-interventions-interrupt-or-reduce-spread-respiratory-viruses-review), which underlined how the results of the \
     	study were inconclusive, as well as [another New York Times op-ed](https://www.nytimes.com/2023/03/10/opinion/masks-work-cochrane-study.html) discussing that statement were issued but they \
      	had little impact on the spread of misleading content on Facebook and Twitter.", unsafe_allow_html=True)
	st.write("Nonetheless, by the time the statement and second op-ed were published, inaccurate versions of the study findings had received at least 27 million impressions on Twitter, several million \
	views on YouTube, and tens of thousands of interactions on Facebook across multiple languages.")
	st.write("In this case study, we track the spread of content, including media reports, related to the findings of the Cochrane study on Twitter, Facebook and YouTube. It shows how poorly worded \
  	communications products can result in misleading coverage. In our networked information ecosystem, clarifying statements or corrections stand little chance of being effective, particularly on \
   	issues that are politicized. And it raises questions about the need for stringent fact checking, even for op-ed pages, as reputable news sources have an outsized role in amplifying the spread of \
    	information.")
	st.write('''It also underlines how academic journals and research publications — the perennial gatekeepers of knowledge — no longer have any room for missteps or errors. On politicized topics \
      	(and unfortunately viruses, masks and vaccines now fall into this category), “trusted” sources of information are increasingly being weaponized by those looking for “credible sources” to support \
       	outlandish claims. The idea that the gold-standard institution for publishing systematic reviews on health care and health policy, Cochrane, was claiming any type of ambiguity around the \
	effectiveness of masks was so surprising. And among reporters without a solid understanding of the limitations of Randomly Controlled Trials (RCTs), the suggestion in the faulty abstract — that \
 	there was insufficient evidence to support a conclusion that masks work — was understood by too many as "masks don't work."''')
	st.write("As more studies and preprints are published and disseminated across social media — where catchy headlines and cherry-picked evidence that aligns with certain views get clicks and \
   	traffic — the risk of academic papers being taken out of context, misinterpreted, and then taken as fact will continue to be a major obstacle to building consensus around public health efforts.")


content_column_2 = st.columns((1, 2, 1))[1]

# Add a header and a text paragraph under the title within the centered column
with content_column_1:
	st.header('Methodology')
	st.write("For analyzing social media conversations, we gathered all the tweets, posts and videos that included the words cochrane and mask between January 29, 2023 and April 1, 2023, using the \
 	APIs of Twitter, Facebook and YouTube. The data resulted in thousands of tweets and posts. Because of this, we opted to focus on those tweets and posts that generated 80 percent of the retweets \
  	(Twitter) and interactions (Facebook). Focusing on high-engagement posts allows us to capture accounts that [make up a disproportionately large share of content views and generally have an \
   	outsized impact](https://healthfeedback.org/misinformation-superspreaders-thriving-on-musk-owned-twitter/) on social media conversations.")
	st.write("To analyze news media coverage, we used the media analytics platform Meltwater (searching for the combination of *mask* AND *cochrane*) and scraped Altmetric (an analytics platform that \
 	tracks mentions of academic articles on the web). We gathered 152 news stories and Substack articles published between January 29 and April 1, 2023 addressing the Cochrane study.")
	


# y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='news_stories')

# news_stories = pd.read_csv("news_stories_final_april26.csv")


# scatter(news_stories)

content_column_3 = st.columns((1, 2, 1))[1]
with content_column_3:
	st.header('Findings')
	st.subheader("Misleading Content and Media Stories Dominate Facebook and Twitter Engagement")
	st.write("Of the 152 news stories we identified, 70 percent provided an incomplete analysis of the actual findings of the study or misrepresented them altogether. In such cases, \
 	news stories would often present the study as evidence that masks are ineffective against Covid-19 or would fail to mention the tenuousness of the evidence and the limitations of the study. \
  	Content inaccurately depicting the findings received 6.4 times more retweets on Twitter and 3.4 times more interactions on Facebook than accurate content. None of the content we reviewed \
   	received a fact check despite a clarifying statement from Cochrane on March 10, 2023.") 
	st.subeader("Influential Misinformation Spreaders Operate Across Multiple Platforms")
	st.write("Some of the same personalities who posted content about the Cochrane review on Substack were also active across multiple social media platforms. For instance, Vinay Prasad was \
 	among several people and entities that posted misleading content about the study across YouTube, Twitter and Facebook.")
	st.subheader("Substack as an Early Amplifier of Misinterpreted Findings")
	st.write("The online publishing platform Substack played a large role early on in spreading misleading narratives about the Cochrane study. Over 90 percent of the 28 Substack articles we identified \
 	inaccurately presented the study findings. The articles were primarily from controversial figures known for spreading misinformation about Covid-19 and public health policy during the pandemic.")
	st.subheader("Disproportionate Influence of a Few Accounts")
	st.write("A handful of Twitter and Facebook accounts were responsible for 80 percent of the retweets and interactions, respectively. Misleading content from these accounts moved quicker and \
 	more broadly on social media than did accurate accounts of the study findings.")
	st.subheader("Stephens’ NYT op-ed a Major Amplifier of False Narratives")
	st.write("While the ratio of inaccurate to accurate posts was around 5:1 on Twitter before the publication of Bret Stephens' Feb. 21, 2023 New York Times op-ed, his piece resulted in a \
 	massive spike in interactions on both Twitter and Facebook, with people sharing or commenting on the story. This news story created the biggest spike of any publication writing about the \
  	cochrane study in our dataset.")
	st.subheader("Multi-Language Spread of Misinformation on Facebook")
	st.write("Misleading information about the Cochrane study on Facebook was not confined to English. It spread across multiple languages, including Albanian, Arabic, Bosnian, Finnish, French, \
 	German, Hungarian, Japanese, Korean, Russian and Swedish, underscoring its global reach.")
	st.subheader("Inaccurate Content on YouTube Gets a Disproportionate Number of Views")
	st.write("The disparity between content inaccurately reporting on the Cochrane findings and accurate reporting was particularly pronounced on YouTube. Inaccurate videos attracted nearly 38.5 times more views than accurate videos, contributing significantly to the spread \
 	of misinformation.")
	st.subheader("Polarized Sharing of News Articles on Twitter")
	st.write("A clear polarization was identified in the communities sharing links to news stories about the Cochrane study. With minimal crossover between those sharing accurate and misleading \
 	narratives, the data indicates users were mostly exposed to, or chose to consume, a single narrative, with misleading narratives having an outsized impact.")

content_column_4 = st.columns((1, 2, 1))[1]
with content_column_4:
	st.header("Tracking the spread of content related to the Cochrane study on Twitter, Facebook and YouTube")
	st.write("In the following section, we provide the details of a data analysis that examined the top content — in terms of engagement, such as views, impressions and interactions — on Twitter, \
 	Facebook and YouTube related to the findings of the Cochrane study. In a subsequent section, we will look specifically at the social media engagement generated by online news stories \
  	reporting on the study. This first section, however, looks specifically at the top-performing content, which can but doesn’t necessarily also include online news stories.")
	st.subheader("Methodology")
	st.write("The posts we scraped were organized into several spreadsheets. We then had several researchers inspect each of the posts to ensure that they were related to the Cochrane study and not \
 	false positives. The researchers also coded the posts as either *misleading* or *nuanced_accurate*. Posts were coded *misleading* if, according to the Cochrane clarification, they framed the study \
  	results as evidence that masks or masking policies during Covid were ineffective or didn’t work. Posts were also coded *misleading* if they failed to provide information about how the results \
   	of the study were inconclusive. Posts that provided these details, not necessarily that masks are effective, but that the study lacks evidence to say one way or the other, were coded as \
    	*nuanced_accurate*.")
	st.write("The following scatterplots chronologically plot engagement around the Cochrane study on Twitter, Facebook and YouTube. You can hover over the nodes in the plot to see more details \
 	and you can click on the link in the nodes to open the tweet, post or video. The nodes are sized based on the number ofimpressions or retweets they have received — the larger the node, \
  	the more impressions, retweets, interactions or views. The x axis represents the days between January 29 and April 2023, and the y axis is the cumulative amount of engagement.")
	st.subheader("Twitter")
	st.write("1 percent of accounts tweeting about the Cochrane study accounted for 80 percent of retweets, highlighting the disproportionate impact a handful of accounts had on the overall \
 	conversation. Among these top tweeters, accounts that distorted, misread or failed to properly frame the study's findings outpaced those that accurately communicated the study results. \
  	In total, there were 272 tweets from accounts inaccurately portraying the study's results, garnering 158,000 retweets and 32 million impressions, while 89 tweets from accounts accurately \
   	conveying the findings generated 25,000 retweets and 13 million impressions. In other words, for every accurate tweet, there were three erroneous ones. These misleading tweets had a \
    	significantly broader reach and attracted more engagement, amassing 6.4 times more retweets and 2.5 times more impressions than their accurate counterparts.") 

top_tweets = pd.read_csv('99th_percentile_tweets_april27.csv')

y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='tweets')

scatter(top_tweets)

	st.write('''Bret Stephens’ February 21, 2023 New York Times op-ed, headlined “The Mask Mandates Did Nothing. Will Any Lessons Be Learned?” created a large jump in engagement \
 	and amplified the false narrative that masks are ineffective. But even before publication of the piece, content inaccurately interpreting the study was hurtling ahead of accurate \
  	content on Twitter. Between January 30, 2023, when the Cochrane study was published, and the date of Stephens' piece, the ratio of inaccurate posts to accurate ones was almost 5:1, \
   	receiving 15 times more retweets and 5.4 times more impressions.''')

	


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









