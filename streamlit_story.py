import streamlit as st
import pandas as pd
import numpy as np
import json
import streamlit.components.v1 as components
import altair as alt

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
