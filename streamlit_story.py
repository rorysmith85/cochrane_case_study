import streamlit as st
import pandas as pd
import numpy as np
import json
import streamlit.components.v1 as components
import altair as alt
# import networkx as nx
# from pyvis.network import Network
from streamlit.components.v1 import html
# import community as community_louvain
# import matplotlib.cm as cm
import re
# from stvis import pv_static
# from pyvis.options import vis_options


# st.set_page_config(layout="wide", initial_sidebar_state="expanded")

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


st.write(
	"""
	<style>
		.narrow-text {
			max-width: 800px;
			margin-left: auto;
			margin-right: auto;
		}
	</style>
	""",
	unsafe_allow_html=True,
)

# Add a container with the 'narrow-text' CSS class
with st.container() as text_container:
	st.markdown(
		'<div class="narrow-text">The governing Coalition had left a trail of death and destruction, both figuratively and literally. Thousands of homes were destroyed, dozens of lives lost, 24 million hectares burned, and Australia was shunned from an international climate summit over the then prime minister Scott Morrison’s climate intransigence. Meanwhile, the rightwing Murdoch media machine continued to spew climate disinformation, cynically blaming the devastation on arson and “back-burning”. Things appeared pretty bleak. Yet at the same time, I sensed that something had changed.</div>',
		unsafe_allow_html=True,
	)


st.title('The Cochrane Mask Study')

# Add a header and a text paragraph under the title
st.header('Why are we doing this?')
st.write('Throughout the pandemic we have seen how newly-published preprints oftentimes muddied conversations related to Covid-19 instead of clarifying them, creating \
evermore confusion among the public and allowing spaces to open up that would be targeted by entities invested in downplaying the disease.')

st.subheader('Tracking the media spread')
st.write('This is a paragraph of text in section 2.')

news_stories = pd.read_csv("news_stories_final_april21.csv")

y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='news_stories')

scatter(news_stories)


# Add a subheader and another text paragraph under the second section followed by scatter plot
st.subheader('The top tweets during this time')
st.write('This is a paragraph of text in section 2.')

top_tweets = pd.read_csv('99th_percentile_tweets.csv')

y_axis = st.selectbox("Select the metric you are interested in:", options=["impressions_cumulative", "retweets_cumulative"], key='tweets')

scatter(top_tweets)


st.subheader('Nytimes articles')
st.write('This is a paragraph of text in section 2.')


# def create_network(df):
# 	G = nx.Graph()

# 	# df['retweets'] = pd.to_numeric(df['retweets'])

# 	for index, row in df.iterrows():
# 		username = row['username']
# 		retweets = row['retweets']
# 		tweet = row['tweet']
# 		G.add_node(username, retweets=retweets, tweet=tweet)
# 		G.add_edge(username, row['original_link'])

# 	net = Network(height='465px', width='100%', notebook=True, bgcolor='#222222', font_color='white')

# 	# for index, row in df.iterrows():
# 	#     username = row['username']
# 	#     retweets = row['retweets']
# 	#     tweet = row['tweet']
# 	#     net.add_node(username, title=f"{username}<br>Retweets: {retweets}<br>Tweet: {tweet}")

# 	net.from_nx(G)
# 	net.barnes_hut(overlap=1)
# 	net.repulsion(node_distance=800, central_gravity=0.01, spring_length=150)

# 	partition = community_louvain.best_partition(G)
# 	unique_communities = len(set(partition.values()))
# 	# color_map = cm.get_cmap('viridis', unique_communities)
# 	color_mapping = {0: "#32CD32", 1: "#FF7F7F"}

# 	for node in net.nodes:
# 		community_id = partition[node['id']]
# 		node['color'] = color_mapping[community_id]
# 		# node['color'] = cm.colors.to_hex(color_map(partition[node['id']] / unique_communities))
# 		if 'retweets' in node:
# 			node['size'] = node['retweets'] / 10
# 			tweet = node['tweet']
# 			node['title'] = f"Tweet: {tweet}"
# 			# print(node)

# 	# options_str = json.dumps(options)
# 	# net.set_options(options_str)
# 	net.show_buttons(filter_='physics')
# 	return net

# nyt = pd.read_csv(path + 'nytimes_articles.csv')

# Create the network using the create_network function
# net = create_network(nyt)
# options = r'var options = {"edges": {"color": {"inherit": true},"smooth": false},"physics": {"enabled": false,"minVelocity": 0.75}}'
# net.set_options(options)

# Save the network as an HTML file
# net.save_graph("nty_network.html")

# In the Streamlit app, display the HTML file with the network visualization
st.title("Network Visualization")
st.markdown("This is a network visualization of the nytimes pieces:")
# net.save_graph(f'{path}/nytimes_graph.html')

HtmlFile = open('nytimes_graph.html', 'r', encoding='utf-8')

# HtmlFile = net.get_html()

chart_container = st.container()

	# Display the centered chart in Streamlit using the container
with chart_container:
	st.write(
		"""
		<style>

			canvas {
				width:1400px;
			}

			#mynetwork {
				width:1400px;
			}

			.element-container {
				display: flex;
				justify-content: center;
			}
		</style>
		""",
		unsafe_allow_html=True,
	)


	html(HtmlFile.read(), height=500, width=1400)


st.title("Network Visualization")
st.markdown("This is a network visualization of the nytimes pieces:")
