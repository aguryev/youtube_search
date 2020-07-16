from xlsxwriter import Workbook
import re
import requests
import json
from datetime import datetime

class Scrapper:
	#
	# YouTube Scrapper
	#

	base_url = 'https://www.youtube.com'

	def __init__(self, keywords, results_amount=100, search_video=True, language_code='en'):
		#
		# initialize Scrapper with a keyword
		#

		self.search_query = '+'.join(keywords)
		self.results_amount = results_amount
		self.search_video = search_video
		self.language_code = language_code
		self.headers = {'Accept-Language': f'{language_code};q=0.8'}
		self.results = []
		self.users = set()


	def search(self):
		#
		# search for videos matching the keyword
		#

		page = 1
		max_pages = (self.results_amount // 20) * 2
		while len(self.results) < self.results_amount or page <= max_pages:
			#print(f'Get page {page}')
			youtube_search = requests.get(f'{self.base_url}/results?search_query={self.search_query}&page={page}', headers=self.headers)
			try:
				# get serch results data
				data = re.search(r'window\["ytInitialData"\]\s*=\s*(.*)', youtube_search.text)

				# parse data
				if self.search_video:
					# video
					self.results += self.parse_videos(json.loads(data.group(1).strip()[:-1]))
				else:
					# users
					self.results += self.parse_users(json.loads(data.group(1).strip()[:-1]))
			
			except Exception as e:
				# skip page
				#print(f'ERROR: {e}')
				pass

			page += 1

		# export results
		if self.search_video:
			self.export_videos()
		else:
			self.export_users()


	def parse_videos(self, data):
		#
		# extracts video data from a search list
		#

		video_list = []

		for item in data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']:
			try:
				# screen streams
				if 'streamed' in item['videoRenderer']['publishedTimeText']['simpleText'].lower():
					raise Exception('Stream!')

				item['videoRenderer'].get('lengthText')

				video_id = item['videoRenderer']['videoId']
				owner = item['videoRenderer']['ownerText']['runs'][0]['text']

				# get video page
				video_page = requests.get(f'{self.base_url}/watch?v={video_id}', headers=self.headers)
				
				# extract data
				data = re.search(r'window\["ytInitialData"\]\s*=\s*(.*)', video_page.text)
				data = json.loads(data.group(1).strip()[:-1])
				video_item = data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
				
				# get views
				views = None
				views_re = re.search(r'(\d+[,\s]?)+', video_item['viewCount']['videoViewCountRenderer']['viewCount']['simpleText'])
				if views_re:
					views = views_re.group(0).strip()

				# get published date
				published = video_item['dateText']['simpleText']
				if 'live' in published:
					with open('live.json', 'w') as f:
						json.dump(item, f)

				video_list.append({
					'id': video_id,
					'owner': owner,
					'published': published,
					'views': views,
				})

				# show status message
				print(f'Added video {len(video_list) + len(self.results)}')
			
			except Exception as e:
				# skip not-video item
				#print(f'ERROR: {e}')
				pass				

			# check collected amount
			if len(video_list) + len(self.results) >= self.results_amount:
				return video_list

		return video_list


	def parse_users(self, data):
		#
		# extracts owners data from a search list
		#

		user_list = []

		for item in data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']:
			try:
				user = item['videoRenderer']['ownerText']['runs'][0]['text']
				if user in self.users:
					raise Exception(f'User {user} exists')

				
				# get user page
				user_url = item['videoRenderer']['ownerText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
				user_page = requests.get(f'{self.base_url}{user_url}', headers=self.headers)

				# extract data
				data = re.search(r'window\["ytInitialData"\]\s*=\s*(.*)', user_page.text)
				data = json.loads(data.group(1).strip()[:-1])

				# get subscribers
				subscribers = re.search(r'\d+([\.,]\d+)?\w?', data['header']['c4TabbedHeaderRenderer']['subscriberCountText']['runs'][0]['text'])

				user_list.append({
					'user': user,
					'subscribers': subscribers.group(0).strip(),
					'url': user_url,
				})

				# add user to the list of known users
				self.users.add(user)

				# show status message
				print(f'Added user {len(user_list) + len(self.results)}')

			except Exception as e:
				#print(f'ERROR: {e}')
				pass

			# check collected amount
			if len(user_list) + len(self.results) >= self.results_amount:
				return user_list

		return user_list

	def export_videos(self):
		#
		# export video results to Excel
		#

		# create workbook
		filename = datetime.now().strftime('videos_%Y%m%d_%H%M%S.xlsx')
		workbook = Workbook(filename)
		
		# set formats
		text_bold = workbook.add_format({'bold': True})

		# add sheet
		sheet = workbook.add_worksheet('Videos')
		sheet.set_column(first_col=0, last_col=0, width=25)
		sheet.set_column(first_col=2, last_col=3, width=15)
		sheet.set_column(first_col=4, last_col=4, width=50)

		# write headers
		headers = [
			'Youtuber',
			'Language',
			'Views',
			'Published',
			'Link',
		]
		for col, title in enumerate(headers):
			sheet.write(0, col, title, text_bold)

		#write data
		for row, item in enumerate(self.results, 1):
			sheet.write(row, 0, item['owner'])
			sheet.write(row, 1, self.language_code)
			sheet.write(row, 2, item['views'])
			sheet.write(row, 3, item['published'])
			sheet.write(row, 4, f'{self.base_url}/watch?v={item["id"]}')

		# save workbook
		workbook.close()
		print(f'Data saved to: {filename}')

	def export_users(self):
		#
		# export user results to Excel
		#

		# create workbook
		filename = datetime.now().strftime('users_%Y%m%d_%H%M%S.xlsx')
		workbook = Workbook(filename)
		
		# set formats
		text_bold = workbook.add_format({'bold': True})

		# add sheet
		sheet = workbook.add_worksheet('Users')
		sheet.set_column(first_col=0, last_col=0, width=25)
		sheet.set_column(first_col=3, last_col=4, width=50)

		# write headers
		headers = [
			'Youtuber',
			'Language',
			'Subscribers',
			'Link',
		]
		for col, title in enumerate(headers):
			sheet.write(0, col, title, text_bold)

		#write data
		for row, item in enumerate(self.results, 1):
			sheet.write(row, 0, item['user'])
			sheet.write(row, 1, self.language_code)
			sheet.write(row, 2, item['subscribers'])
			sheet.write(row, 3, f'{self.base_url}{item["url"]}')

		# save workbook
		workbook.close()
		print(f'Data saved to: {filename}')



	def show(self):
		#
		# shows search results
		#
		print(json.dumps(self.results, indent=2))


if __name__ == '__main__':
	#
	# main program
	#

	# parse arguments
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--keywords', help='Search keywords', type=str, nargs='*')
	parser.add_argument('--target', default='video',  help='Search target: video or users', type=str)
	parser.add_argument('--lang', default='en', help='Search language', type=str)
	parser.add_argument('--amount', default=100, help='Number of search results', type=int)

	args = parser.parse_args()

	# make search
	scrapper = Scrapper(
		keywords=args.keywords,
		results_amount=args.amount,
		search_video=(args.target=='video'),
		language_code=args.lang,
	)
	scrapper.search()

















