######################################################################################
#
#	rawrANIME (BY TEHCRUCIBLE) - v0.05
#
######################################################################################

TITLE = "rawrANIME"
PREFIX = "/video/rawranime"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_QUEUE = "icon-queue.png"
ICON_WATCHED = "icon-watched.png"
ICON_MARK = "icon-mark.png"
ICON_MARKALL = "icon-markall.png"
ICON_UNMARKALL = "icon-unmarkall.png"
ICON_LISTALL = "icon-listall.png"
ICON_HASH = "icon-hash.png"
BASE_URL = "http://rawranime.tv"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
	PopupDirectoryObject.thumb = R(ICON_COVER)
	PopupDirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_COVER)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = 'http://rawranime.tv/'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(LatestCategory, title="Latest Episodes"), title = "Latest Episodes", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ChooseAlphabetically, title="All Anime", category = "/list/listmode"), title = "All Anime", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ChooseAlphabetically, title="Ongoing Anime", category = "/list/ongoing"), title = "Ongoing Anime", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ChooseAlphabetically, title="Movies", category = "/list/movies"), title = "Movies", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Top Rated", category = "/list/toprated"), title = "Top Rated", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Most Popular", category = "/list/popular"), title = "Most Popular", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Most Popular Ongoing", category = "/list/popularongoing"), title = "Most Popular Ongoing", thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Bookmarks"), title = "My Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(InputDirectoryObject(key=Callback(Search), title = "Search", prompt = "Search for anime?", thumb = R(ICON_SEARCH)))
	
	return oc

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title, no_cache = True)
	
	for each in Dict:
		show_url = Dict[each]
		page_data = HTML.ElementFromURL(show_url)
		show_title = each
		show_thumb = BASE_URL + page_data.xpath("//div[@class='anime_info']//img/@data-original")[0]
		show_summary = page_data.xpath("//div[@class='anime_info_synopsis']/text()")[0]
		
		oc.add(DirectoryObject(
			key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
			title = show_title,
			thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
			summary = show_summary
			)
		)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	return oc	

######################################################################################
# Takes query and sets up a http request to return and create objects from results

@route(PREFIX + "/search")	
def Search(query):
		
	oc = ObjectContainer(title1 = query)
	
	#setup the search request url
	request_url = "http://rawranime.tv/index.php?app=core&module=search&section=search&do=search&fromsearch=1"
	referer = "http://rawranime.tv/index.php?app=core&module=search&do=search&fromMainBar=1"
	values = {
		'search_app':'anime',
		'search_term':query,
		'search_app':'anime',
		'andor_type':'and',
		'search_content':'both',
		'search_author':'',
		'search_date_start':'',
		'search_date_end':'',
		'search_app_filters[core][sortKey]':'date',
		'search_app_filters[core][sortDir]':'0',
		'search_app_filters[forums][noPreview]':'1',
		'search_app_filters[forums][pCount]':'',
		'search_app_filters[forums][pViews]':'',
		'search_app_filters[forums][sortKey]':'date',
		'search_app_filters[forums][sortDir]':'0',
		'search_app_filters[calendar][sortKey]':'date',
		'search_app_filters[calendar][sortDir]':'0',
		'submit':'Search Now'
		}

	#do http request for search data
	page_data = HTML.ElementFromString(HTTP.Request(request_url, values = values, headers={'referer':referer}))

	for each in page_data.xpath("//div[@id='search_results']//li"):

		show_url = each.xpath(".//a/@href")[0]
		show_title = each.xpath(".//a/text()")[0].strip()
		show_thumb = BASE_URL + each.xpath(".//img/@src")[0]
		show_summary = each.xpath(".//h4/text()")[0]
		
		oc.add(DirectoryObject(
			key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
			title = show_title,
			thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
			summary = show_summary
			)
		)
	
	#check for zero results and display error
	if len(oc) < 1:
		Log ("No shows found! Check search query.")
		return ObjectContainer(header="Error", message="Nothing found! Try something less specific.", no_cache = True)
	
	return oc	
	
######################################################################################
# Creates latest episode objects from the front page

@route(PREFIX + "/latestcategory")	
def LatestCategory(title):

	oc = ObjectContainer(title1 = title, no_cache = True)
	page_data = HTML.ElementFromURL(BASE_URL)
	eps_list = page_data.xpath("//div[@class='new_episode']")

	for each in eps_list:
		ep_url = each.xpath("./h5/a/@href")
		episode = each.xpath("./h3/text()")[0].strip() + " - " + each.xpath("./h4/b/text()")[0].strip()
		ep_title = each.xpath("./h4/b/text()")[0].strip()
		show_title = each.xpath("./h3/text()")
		
		oc.add(PopupDirectoryObject(
			key = Callback(GetMirrors, ep_url = ep_url, ep_title = ep_title, show_title = show_title),
			title = episode,
			thumb = Callback(GetThumb, ep_url = ep_url)
			)
		)
	
	#check for results and display an error if none
	if len(oc) < 1:
		Log ("No shows found! Check xpath queries.")
		return ObjectContainer(header="Error", message="Error! Please let TehCrucible know, at the Plex forums.", no_cache = True)
	
	return oc	
		
######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category):

	oc = ObjectContainer(title1 = title, no_cache = True)
	page_data = HTML.ElementFromURL(BASE_URL + category)

	for each in page_data.xpath("//tr[contains(@class, 'list ')]"):

		show_url = each.xpath("./td[@class='animetitle']/a/@href")[0]
		show_title = each.xpath("./td[@class='animetitle']/a/text()")[0].strip()
		show_thumb = BASE_URL + each.xpath("./td//img/@data-original")[0]
		
		oc.add(DirectoryObject(
			key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
			title = show_title,
			thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
			summary = "Watch " + show_title + " in HD now from rawrANIME.tv!"
			)
		)
	
	#check for results and display an error if none
	if len(oc) < 1:
		Log ("No shows found! Check xpath queries.")
		return ObjectContainer(header="Error", message="Error! Please let TehCrucible know, at the Plex forums.", no_cache = True)
	
	return oc
	
######################################################################################
# Choose show or movie alphabetically

@route(PREFIX + "/choosealphabetically")
def ChooseAlphabetically(title, category):

	oc = ObjectContainer(title1 = title, no_cache = True)
	page_data = HTML.ElementFromURL(BASE_URL + category)
	show_letters = page_data.xpath("//td[contains(@class, 'listletter')]/a/text()")
	category_title = title
		
	oc.add(DirectoryObject(
		key = Callback(ShowCategorySorted, title = "List All", category = category, category_title = category_title),
		title = "List All", 
		thumb = R(ICON_LISTALL)
		)
	)
	
	for letter in show_letters:
		ICON_ALPHA = "icon-" + letter.upper() + ".png"

		if letter == "#":
			oc.add(DirectoryObject(
			key = Callback(ShowCategorySorted, title = letter, category = category, category_title = category_title),
			title = letter,
			thumb = R(ICON_HASH)
			)
		)
		else:
			oc.add(DirectoryObject(
				key = Callback(ShowCategorySorted, title = letter, category = category, category_title = category_title),
				title = letter,
				thumb = R(ICON_ALPHA)
				)
			)
		
	return oc
		
################################################################################################
# Creates page url from category and creates objects from that page sorting them alphabetically

@route(PREFIX + "/showcategorysorted")	
def ShowCategorySorted(title, category, category_title):

	oc = ObjectContainer(title1 = '%s > %s' % (category_title, title), no_cache = True)
	page_data = HTML.ElementFromURL(BASE_URL + category)
	list_all = "List All"
	list_category = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','W','Y','Z')
		
	for each in page_data.xpath("//tr[contains(@class, 'list ')]"):

		show_url = each.xpath("./td[@class='animetitle']/a/@href")[0]
		show_title = each.xpath("./td[@class='animetitle']/a/text()")[0].strip()
		show_thumb = BASE_URL + each.xpath("./td//img/@data-original")[0]
		
		if title == list_all:
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
				title = show_title,
				thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
				summary = "Watch " + show_title + " in HD now from rawrANIME.tv!"
				)
			)		
		elif show_title[0].upper() == title:
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
				title = show_title,
				thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
				summary = "Watch " + show_title + " in HD now from rawrANIME.tv!"
				)
			)
		elif show_title[0].upper() not in list_category and title not in list_category:
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, show_title = show_title, show_url = show_url),
				title = show_title,
				thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
				summary = "Watch " + show_title + " in HD now from rawrANIME.tv!"
				)
			)
		
	#check for results and display an error if none
	if len(oc) < 1:
		Log ("No shows found! Check xpath queries.")
		return ObjectContainer(header="Error", message="Error! Please let TehCrucible know, at the Plex forums.", no_cache = True)
	
	return oc
	
######################################################################################
# Creates an object for every 30 episodes (or part thereof) from a show url

@route(PREFIX + "/pageepisodes")
def PageEpisodes(show_title, show_url):

	oc = ObjectContainer(title1 = show_title, no_cache = True)
	page_data = HTML.ElementFromURL(show_url)
	show_thumb = BASE_URL + page_data.xpath("//div[@class='anime_info']//img/@data-original")[0]
	show_ep_count = len(page_data.xpath("//div[@class='episode_box']"))
	show_summary = page_data.xpath("//div[@class='anime_info_synopsis']/text()")[0]
	eps_list = page_data.xpath("//div[@class='list_header_epnumber']/text()")
	
	#set a start point and determine how many objects we will need
	offset = 0
	rotation = (show_ep_count - (show_ep_count % 30)) / 30

	#add a directory object for every 30 episodes
	while rotation > 0:
	
		start_ep  = offset
		end_ep = offset + 30
		start_ep_title = eps_list[(start_ep)].strip()
		end_ep_title = eps_list[(end_ep - 1)].strip()
		
		oc.add(DirectoryObject(
			key = Callback(ListEpisodes, show_title = show_title, show_url = show_url, start_ep = start_ep, end_ep = end_ep),
			title = "Episodes " + start_ep_title + " - " + end_ep_title,
			thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
#			summary = show_summary
			)
		)
		
		offset += 30
		rotation = rotation - 1
	
	#if total eps is divisible by 30, add bookmark link and return
	if (show_ep_count % 30) == 0:

		#provide a way to add or remove from bookmarks list
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, show_title = show_title, show_url = show_url),
			title = "Add/remove Bookmark",
			summary = "You can add or remove this show from your Bookmarks list.",
			thumb = R(ICON_QUEUE)
			)
		)	
		return oc
	
	#else create directory object for remaining eps
	else:

		start_ep = offset
		end_ep = (offset + (show_ep_count % 30))
		start_ep_title = eps_list[(start_ep)].strip()
		end_ep_title = eps_list[(end_ep - 1)].strip()
		
		oc.add(DirectoryObject(
			key = Callback(ListEpisodes, show_title = show_title, show_url = show_url, start_ep = offset, end_ep = offset + (show_ep_count % 30)),
			title = "Episodes " + start_ep_title + " - " + end_ep_title,
			thumb = Resource.ContentsOfURLWithFallback(url = show_thumb, fallback='icon-cover.png'),
#			summary = show_summary
			)
		)
	
		#provide a way to add or remove from bookmarks list
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, show_title = show_title, show_url = show_url),
			title = "Add/remove Bookmark",
			summary = "You can add or remove this show from your Bookmarks list.",
			thumb = R(ICON_QUEUE)
			)
		)	
		return oc

######################################################################################
# Returns a list of VideoClipObjects for the episodes with a specified range

@route(PREFIX + "/listepisodes")	
def ListEpisodes(show_title, show_url, start_ep, end_ep):

	oc = ObjectContainer(title1 = show_title, no_cache = True)
	page_data = HTML.ElementFromURL(show_url)
	eps_list = page_data.xpath("//div[@class='episode_box']")
	
	for each in eps_list[int(start_ep):int(end_ep)]:
		ep_url = each.xpath(".//a/@href")[0]
		ep_title = "Episode " + each.xpath("./div[@class='list_header_epnumber']/text()")[0].strip() + ": " + each.xpath("./div[@class='list_header_epname']/text()")[0].strip()
		
		# Determine which thumb and title to show, based on if episode has been marked as watched or not
		if Data.Exists(show_title):
			
			watched = []
			watched = Data.LoadObject(show_title)
		
			if ep_title in watched:
				oc.add(DirectoryObject(
				key = Callback(GetMirrors, ep_url = ep_url, ep_title = ep_title, show_title = show_title),
				title = ep_title + " [Watched]",
				thumb = R(ICON_WATCHED)
				)
			)
			else:
				oc.add(DirectoryObject(
				key = Callback(GetMirrors, ep_url = ep_url, ep_title = ep_title, show_title = show_title),
				title = ep_title,
				thumb = R(ICON_COVER)
				)
			)
		else:
			oc.add(DirectoryObject(
			key = Callback(GetMirrors, ep_url = ep_url, ep_title = ep_title, show_title = show_title),
			title = ep_title,
			thumb = R(ICON_COVER)
			)
		)
	
	#add a way to mark all episodes of show as watched
	oc.add(DirectoryObject(
		key = Callback(AddWatchedShow, show_url = show_url, show_title = show_title, start_ep = start_ep, end_ep = end_ep),
		title = "Mark all episodes of this show as watched",
		thumb = R(ICON_MARKALL),
		summary = "This will mark all episodes as watched."
		)
	)
	
	#add a way to remove all watched marks from episodes of show
	oc.add(DirectoryObject(
		key = Callback(RemoveWatchedShow, show_url = show_url, show_title = show_title, start_ep = start_ep, end_ep = end_ep),
		title = "Mark all episodes of this show as unwatched",
		thumb = R(ICON_UNMARKALL),
		summary = "This will mark all episodes as unwatched."
		)
	)
		
	return oc

######################################################################################
# Returns a list of VideoClipObjects for each mirror, with video_id tagged to ep_url

@route(PREFIX + "/getmirrors")	
def GetMirrors(ep_url, ep_title, show_title):

	oc = ObjectContainer(title2 = '%s > %s' % (show_title, ep_title), no_cache = True)
	page_data = HTML.ElementFromURL(ep_url)
	
	for each in page_data.xpath("//if/div[contains(@class, 'mirror')]"):
		video_type = each.xpath("./div/div/@class")[0].split("_trait")[0].capitalize()
		video_quality = each.xpath("./div/div/@class")[1].split("_trait")[0].upper().replace("_"," ")
		video_id = each.xpath("./@rn")[0]
		video_url = 'http:' + String.Quote(ep_url.split(':',1)[1], usePlus=False) + "?" + video_id
		video_thumb = BASE_URL + each.xpath("./img/@src")[0]
		video_host = each.xpath("./text()")[2].strip()
		video_title = video_type + " [" + video_quality + "] (" + video_host + ")"

		oc.add(VideoClipObject(
			url = video_url,
			title = video_title,
			thumb = Callback(GetThumb, ep_url = ep_url)
			)
		)
	
	#provide a way to mark episode as watched or unwatched
	oc.add(DirectoryObject(
		key = Callback(EditWatchedEpisode, ep_title = ep_title, show_title = show_title),
		title = "Mark this episode as watched/unwatched",
		summary = "This will mark this episode as watched/unwatched, making it easier to remember where you left off.",
		thumb = R(ICON_MARK)
		)
	)
		
	return oc
	
######################################################################################
# Get episode thumbnails from the ep_url

@route(PREFIX + "/getthumb")
def GetThumb(ep_url):
	
	ep_data = HTML.ElementFromURL(ep_url)
	find_thumb = BASE_URL + ep_data.xpath("//div[contains(@class, 'selected')]/img/@src")[0]
	
	try:
		data = HTTP.Request(find_thumb, cacheTime=CACHE_1MONTH).content
		return DataObject(data, 'image/png')	
	except:
		return Redirect(R(ICON_COVER))

######################################################################################
# Adds and removes a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(show_title, show_url):
	
	if show_title in Dict:
		del Dict[show_title]
		Dict.Save()
		# remove empty dictionary file
		if not Dict:
			Dict.Reset()
		return ObjectContainer(header=show_title, message='This show has been removed from your bookmarks.', no_cache = True)
	else:
		Dict[show_title] = show_url
		Dict.Save()
		return ObjectContainer(header=show_title, message='This show has been added to your bookmarks.', no_cache = True)
		
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():
	itemsToRemove = []
	for each in Dict:
		itemsToRemove.append(each)
	for each in itemsToRemove:
		show_title = each
		del Dict[show_title]
		Dict.Save()
	# remove empty dictionary file
	Dict.Reset()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list has been cleared.', no_cache = True)
		
######################################################################################
# Adds a show to the watched list

@route(PREFIX + "/addwatchedshow")
def AddWatchedShow(show_url, show_title, start_ep, end_ep):

        page_data = HTML.ElementFromURL(show_url)
        eps_list = page_data.xpath("//div[@class='episode_box']")
        
        for each in eps_list[int(start_ep):int(end_ep)]:
                ep_title = "Episode " + each.xpath("./div[@class='list_header_epnumber']/text()")[0].strip() + ": " + each.xpath("./div[@class='list_header_epname']/text()")[0].strip()
                
                if Data.Exists(show_title):
                        watched = []
                        watched = Data.LoadObject(show_title)
                        
                        if ep_title in watched:
                                Data.SaveObject(show_title, watched)
                        else:
                                watched.insert(0, ep_title)
                                watched.sort()
                                Data.SaveObject(show_title, watched)
                else:
                        watched = []
                        watched.insert(0, ep_title)
                        Data.SaveObject(show_title, watched)
                
        return ObjectContainer(header=show_title, message='All episodes for this show have been marked as watched.', no_cache = True)
               
######################################################################################
# Removes a show from the watched list

@route(PREFIX + "/removewatchedshow")
def RemoveWatchedShow(show_url, show_title, start_ep, end_ep):

	page_data = HTML.ElementFromURL(show_url)
	eps_list = page_data.xpath("//div[@class='episode_box']")
	
	for each in eps_list[int(start_ep):int(end_ep)]:
		ep_title = "Episode " + each.xpath("./div[@class='list_header_epnumber']/text()")[0].strip() + ": " + each.xpath("./div[@class='list_header_epname']/text()")[0].strip()
		
		if Data.Exists(show_title):
			watched = []
			watched = Data.LoadObject(show_title)
			
			if ep_title in watched:
				watched.remove(ep_title)
				Data.SaveObject(show_title, watched)
				if not watched:
					Data.Remove(show_title)

        return ObjectContainer(header=show_title, message='All episodes for this show have been marked as unwatched.', no_cache = True)

######################################################################################
# Adds and removes an episode to the watched list

@route(PREFIX + "/editwatchedepisode")
def EditWatchedEpisode(ep_title, show_title):

        if Data.Exists(show_title):

                watched = []
                watched = Data.LoadObject(show_title)

                if ep_title in watched:
                        watched.remove(ep_title)
                        Data.SaveObject(show_title, watched)
                        if not watched:
                                Data.Remove(show_title)
                        return ObjectContainer(header=ep_title, message='This episode has been removed from your watched list.', no_cache = True)
                else:
                        watched.insert(0, ep_title)
                        watched.sort()
                        Data.SaveObject(show_title, watched)
                        return ObjectContainer(header=ep_title, message='This episode has been added to your watched list.', no_cache = True)
        else:
                watched = []
                watched.insert(0, ep_title)
                Data.SaveObject(show_title, watched)
                return ObjectContainer(header=ep_title, message='This episode has been added to your watched list.', no_cache = True)
