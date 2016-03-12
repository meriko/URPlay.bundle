TITLE  = 'UR Play'
PREFIX = '/video/urplay'

ART  = R('art-default.jpg')
ICON = R('icon-default.png')

BASE_URL = 'http://www.urplay.se'
MOST_VIEWED_URL = BASE_URL + '/sok?product_type=program&query=&type=default&view=most_viewed'
LATEST_URL = BASE_URL + '/sok?product_type=program&query=&type=default&view=latest'
LAST_CHANCE_URL = BASE_URL + '/sok?product_type=program&query=&type=default&view=last_chance'

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

####################################################################################################
def Start():
    # Set the default ObjectContainer attributes
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = ART
    
    DirectoryObject.thumb = ICON

    # Set the default cache time
    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = HTTP_USER_AGENT

####################################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer()

    title = unicode('Senaste')
    oc.add(
        DirectoryObject(
            key = Callback(Episodes, title=title, url=LATEST_URL, thumb=ICON, type='products-search-result'),
            title = title
        )
    )   
    
    title = unicode('Populärast just nu')
    oc.add(
        DirectoryObject(
            key = Callback(Episodes, title=title, url=MOST_VIEWED_URL, thumb=ICON, type='products-search-result'),
            title = title
        )
    )
    
    title = unicode('Sista chansen')
    oc.add(
        DirectoryObject(
            key = Callback(Episodes, title=title, url=LAST_CHANCE_URL, thumb=ICON, type='products-search-result'),
            title = title
        )
    )
    
    title = unicode('Kategorier')
    oc.add(
        DirectoryObject(
            key = Callback(Categories, title = title),
            title = title
        )
    )
    
    title = unicode('Alla Program')
    oc.add(
        DirectoryObject(
            key = Callback(AllProgramsByLetter, title = title),
            title = title
        )
    )
    
    title = unicode("Sök")
    oc.add(
        InputDirectoryObject(
            key = Callback(Search, title = title),
            title  = title,
            prompt = title,
            thumb = ICON
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/Categories')
def Categories(title):
    oc = ObjectContainer(title2 = unicode(title))
    
    element = HTML.ElementFromURL(BASE_URL)
    
    for item in element.xpath("//*[@id='categories']/a"):
        title = unicode(item.xpath(".//span/text()")[0])
        url = BASE_URL + item.xpath("./@href")[0]
        thumb = BASE_URL + item.xpath(".//img/@data-src")[0]
        
        oc.add(
            DirectoryObject(
                key = Callback(Episodes, title=title, url=url, thumb=thumb, type='products-search-result'),
                title = title,
                thumb = thumb
            )
        )
        
    return oc
    
def Category(title, url, thumb):
    pass

####################################################################################################
@route(PREFIX + '/AllPrograms')
def AllProgramsByLetter(title):
    oc = ObjectContainer(title2 = unicode(title))
    
    element = HTML.ElementFromURL(BASE_URL + '/sok?product_type=series&rows=999&start=0')
    
    for program in element.xpath("//*[@class='series']/a"):
        url = BASE_URL + program.xpath("./@href")[0]
        title = unicode(program.xpath(".//h3/text()")[0])
        
        try:
            thumb = program.xpath(".//img/@data-src")[0]
        except:
            thumb = None
        
        try:
            summary = program.xpath(".//*[@class='description']/text()")[0]
        except:
            summary = None
        
        try:
            episode_count = int(''.join(program.xpath(".//*[@class='counter']//text()")).strip())
        except:
            episode_count = None
        
        oc.add(
            TVShowObject(
                key = Callback(Episodes, url = url, title = title, thumb = thumb),
                rating_key = url,
                title = title,
                thumb = thumb,
                summary = summary,
                episode_count = episode_count
            )
        )
    
    return oc

####################################################################################################
@route(PREFIX + '/Episodes')
def Episodes(url, title, thumb, type='episodes'):

    show = unicode(title)
    art = thumb
    oc = ObjectContainer(title2 = show)
    element = HTML.ElementFromURL(url)
    
    for episode in element.xpath("//*[@id='%s']//li" % type):
        episode_url = BASE_URL + episode.xpath(".//a/@href")[0]
        episode_title = unicode(episode.xpath(".//h3/text()")[0])
        
        try:
            episode_thumb = episode.xpath(".//img/@data-src")[0]
        except:
            episode_thumb = None
        
        try:
            episode_summary = episode.xpath(".//*[@class='description']/text()")[0]
        except:
            episode_summary = None
            
        oc.add(
            VideoClipObject(
                url = episode_url,
                title = episode_title,
                thumb = episode_thumb,
                summary = episode_summary,
                art = art
            )
        )
        
    try:
        next_page_url = BASE_URL + element.xpath("//*[@id='next-page']/@href")[0]
        
        oc.add(
            NextPageObject(
                key = Callback(Episodes, url=next_page_url, title=title, thumb=thumb, type=type),
                title = 'Fler...'
            )
        )
    except:
        pass
        
    return oc

####################################################################################################
@route(PREFIX + '/Search')
def Search(query, title):
    oc = ObjectContainer(title2 = unicode(title))

    result = Episodes(
        url = BASE_URL + '/sok?product_type=program&view=&age=&type=&query=' + String.Quote(query),
        title = unicode('Resultat för : "') + query + '"',
        thumb = ICON,
        type = 'products-search-result'
    )
    
    if len(result) > 0:
        return result
    else:
        oc.header  = unicode('Inga program funna')
        oc.message = unicode('Din sökning på : "') + query + '" gav inget resultat'
        return oc
